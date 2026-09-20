import os
import time

import truststore
from dotenv import load_dotenv

# Usa o armazenamento de certificados do sistema (funciona em redes com
# interceptação SSL/VPN corporativa, sem desativar a verificação).
truststore.inject_into_ssl()
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Carrega as variáveis de ambiente do arquivo .env (API key, conexão, etc.)
load_dotenv()

# Caminho do arquivo PDF (configurado no .env)
PDF_PATH = os.getenv("PDF_PATH", "document.pdf")

# String de conexão com o PostgreSQL (mesmo padrão do docker-compose.yml)
DB_CONNECTION = os.getenv(
    "DB_CONNECTION",
    "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
)

# Nome da coleção (tabela) criada no banco vetorial
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "desafio_ingestao_busca")


def ingest_pdf():
    # 1. Carrega o conteúdo do PDF
    loader = PyPDFLoader(PDF_PATH)
    documentos = loader.load()
    print(f"PDF carregado: {len(documentos)} página(s) lida(s).")

    # 2. Divide o texto em chunks de 1000 caracteres com 150 de sobreposição
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = text_splitter.split_documents(documentos)
    print(f"Texto dividido em {len(chunks)} chunk(s).")

    # 3. Modelo de embeddings do Google (gera o vetor de cada chunk)
    #    transport="rest": usa HTTP em vez de gRPC (funciona em redes com
    #    certificado corporativo, já que o truststore corrige o SSL do HTTP)
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        transport="rest",
    )

    # 4. Conecta no PostgreSQL + pgVector e salva os vetores no banco
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
    )

    # Envia em lotes pequenos: a camada gratuita do Google limita quantos
    # textos podem ser vetorizados por requisição.
    BATCH_SIZE = 20
    for inicio in range(0, len(chunks), BATCH_SIZE):
        lote = chunks[inicio : inicio + BATCH_SIZE]
        vector_store.add_documents(lote)
        print(f"  ... {min(inicio + BATCH_SIZE, len(chunks))}/{len(chunks)} chunks salvos")
        time.sleep(2)  # respeita o limite de requisições por minuto

    print(
        f"Ingestão concluída! {len(chunks)} vetores salvos "
        f"na coleção '{COLLECTION_NAME}'."
    )


if __name__ == "__main__":
    ingest_pdf()
