import os
import sys
import time

from dotenv import load_dotenv
from google import genai
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

# --- Controle de rate limit da API de embeddings ---
RATE_LIMIT_TPM = 30_000      # tokens por minuto (limite da API Google)
CHARS_PER_TOKEN = 4           # estimativa conservadora (recomendação Google)
SAFETY_MARGIN = 0.80          # usar apenas 80% do limite para margem de segurança



def _count_tokens_api(client: genai.Client, texts: list[str], model_name: str) -> int:
    """Usa a API do Google para retornar o número exato de tokens da lista de textos."""
    if not texts:
        return 0
    response = client.models.count_tokens(model=model_name, contents=texts)
    return response.total_tokens


def _build_batches(client: genai.Client, chunks, model_name: str) -> list[list]:
    """
    Agrupa chunks em lotes dinâmicos que respeitam o rate limit.
    Cada lote consome no máximo RATE_LIMIT_TPM * SAFETY_MARGIN tokens estimados.
    """
    max_tokens_per_batch = int(RATE_LIMIT_TPM * SAFETY_MARGIN)
    batches = []
    current_batch = []
    current_tokens = 0

    for chunk in chunks:
        # Conta e adiciona o tamanho real
        chunk_tokens = _count_tokens_api(client, [chunk.page_content], model_name)
        if current_batch and (current_tokens + chunk_tokens) > max_tokens_per_batch:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0
        current_batch.append(chunk)
        current_tokens += chunk_tokens

    if current_batch:
        batches.append(current_batch)

    return batches


def ingest_pdf():
    """Carrega o PDF, divide em chunks, gera embeddings e salva no PGVector."""

    # Valida variáveis obrigatórias
    if not DATABASE_URL:
        print("ERRO: DATABASE_URL não configurada no .env")
        sys.exit(1)
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERRO: GOOGLE_API_KEY não configurada no .env")
        sys.exit(1)
        
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

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

    # Passo 6: Salvar os chunks no banco em lotes (rate limit)
    print("Contabilizando tokens reais via API (isso pode demorar um pouco devido à latência de rede)...")
    batches = _build_batches(client, chunks, EMBEDDING_MODEL)
    total_tokens = _count_tokens_api(client, [c.page_content for c in chunks], EMBEDDING_MODEL)
    print(f"Salvando embeddings no banco de dados...")
    print(f"  -> {len(batches)} lote(s) | {total_tokens} tokens REAIS confirmados | limite: {RATE_LIMIT_TPM} TPM")

    for batch_num, batch in enumerate(batches, 1):
        batch_tokens = _count_tokens_api(client, [c.page_content for c in batch], EMBEDDING_MODEL)
        print(f"  -> Lote {batch_num}/{len(batches)} ({len(batch)} chunks, {batch_tokens} tokens)...", end=" ", flush=True)
        vector_store.add_documents(batch)
        print("OK")

        # Pausa fixa de 60 segundos entre os lotes (exceto no último)
        if batch_num < len(batches):
            print("     Aguardando 60s (rate limit Google API)...", flush=True)
            time.sleep(60)

    print(f"  -> {len(chunks)} chunks salvos com sucesso!")


if __name__ == "__main__":
    ingest_pdf()