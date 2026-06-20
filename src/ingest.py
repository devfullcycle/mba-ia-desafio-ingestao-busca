import os
import sys
import time

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# --- Configuração via variáveis de ambiente ---
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "document_embeddings")
PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")

# --- Controle de rate limit da API de embeddings ---
RATE_LIMIT_TPM = 30_000      # tokens por minuto (limite da API Google)
CHARS_PER_TOKEN = 4           # estimativa conservadora (recomendação Google)
SAFETY_MARGIN = 0.80          # usar apenas 80% do limite para margem de segurança


def _estimate_tokens(text: str) -> int:
    """Estima o número de tokens de um texto usando a proporção chars/token."""
    return len(text) // CHARS_PER_TOKEN


def _build_batches(chunks) -> list[list]:
    """
    Agrupa chunks em lotes dinâmicos que respeitam o rate limit.
    Cada lote consome no máximo RATE_LIMIT_TPM * SAFETY_MARGIN tokens estimados.
    """
    max_tokens_per_batch = int(RATE_LIMIT_TPM * SAFETY_MARGIN)
    batches = []
    current_batch = []
    current_tokens = 0

    for chunk in chunks:
        chunk_tokens = _estimate_tokens(chunk.page_content)
        if current_batch and (current_tokens + chunk_tokens) > max_tokens_per_batch:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0
        current_batch.append(chunk)
        current_tokens += chunk_tokens

    if current_batch:
        batches.append(current_batch)

    return batches


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    reraise=True,
)
def _add_documents_with_retry(vector_store: PGVector, batch: list) -> None:
    """Adiciona documentos ao vector store com retry automático."""
    vector_store.add_documents(batch)


def ingest_pdf() -> None:
    """Carrega o PDF, divide em chunks, gera embeddings e salva no PGVector."""

    # Valida variáveis obrigatórias
    if not DATABASE_URL:
        print("ERRO: DATABASE_URL não configurada no .env")
        sys.exit(1)

    # Passo 1: Carregar o PDF
    print(f"Carregando PDF: {PDF_PATH}")
    try:
        loader = PyPDFLoader(PDF_PATH)
        documents = loader.load()
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado: {PDF_PATH}")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO ao carregar PDF: {e}")
        sys.exit(1)
    print(f"  -> {len(documents)} páginas carregadas.")

    # Passo 2: Dividir em chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"  -> {len(chunks)} chunks gerados.")

    # Passo 3-5: Instanciar embeddings e criar VectorStore
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            connection=DATABASE_URL,
            use_jsonb=True,
        )
    except Exception as e:
        print(f"ERRO ao inicializar embeddings ou conexão com banco: {e}")
        sys.exit(1)

    # Passo 6: Salvar os chunks no banco em lotes (rate limit)
    batches = _build_batches(chunks)
    total_tokens = sum(_estimate_tokens(c.page_content) for c in chunks)
    print(f"Salvando embeddings no banco de dados...")
    print(f"  -> {len(batches)} lote(s) | ~{total_tokens} tokens estimados | limite: {RATE_LIMIT_TPM} TPM")

    for batch_num, batch in enumerate(batches, 1):
        batch_tokens = sum(_estimate_tokens(c.page_content) for c in batch)
        print(f"  -> Lote {batch_num}/{len(batches)} ({len(batch)} chunks, ~{batch_tokens} tokens)...", end=" ", flush=True)
        try:
            _add_documents_with_retry(vector_store, batch)
            print("OK")
        except Exception as e:
            print(f"FALHOU")
            print(f"     ERRO no lote {batch_num}: {e}")
            sys.exit(1)

        # Pausa fixa de 60 segundos entre os lotes (exceto no último)
        if batch_num < len(batches):
            print("     Aguardando 60s (rate limit Google API)...", flush=True)
            time.sleep(60)

    print(f"  -> {len(chunks)} chunks salvos com sucesso!")


if __name__ == "__main__":
    ingest_pdf()