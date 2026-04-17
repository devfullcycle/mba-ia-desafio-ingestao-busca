import os
import sys

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

# --- Configuração via variáveis de ambiente ---
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "document_embeddings")
PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")

# Dimensão do modelo embedding-001 do Google
VECTOR_SIZE = 768


def ingest_pdf():
    """Carrega o PDF, divide em chunks, gera embeddings e salva no PGVector."""

    # Valida variáveis obrigatórias
    if not DATABASE_URL:
        print("ERRO: DATABASE_URL não configurada no .env")
        sys.exit(1)
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERRO: GOOGLE_API_KEY não configurada no .env")
        sys.exit(1)

    # Passo 1: Carregar o PDF
    print(f"Carregando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"  -> {len(documents)} páginas carregadas.")

    # Passo 2: Dividir em chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"  -> {len(chunks)} chunks gerados.")

    # Passo 3: Instanciar o modelo de embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    # Passo 4 e 5: Criar o VectorStore
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )

    # Passo 6: Salvar os chunks no banco
    print("Salvando embeddings no banco de dados...")
    vector_store.add_documents(chunks)
    print(f"  -> {len(chunks)} chunks salvos com sucesso!")


if __name__ == "__main__":
    ingest_pdf()