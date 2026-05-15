import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_DEFAULT_DB = "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip() or _DEFAULT_DB
COLLECTION_NAME = (os.getenv("COLLECTION_NAME") or "").strip() or "documentos"
DEFAULT_PDF = "document.pdf"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
SEARCH_K = 10

EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "5"))
EMBED_BATCH_DELAY_SEC = float(os.getenv("EMBED_BATCH_DELAY_SEC", "8"))

PROVIDER = os.getenv("LLM_PROVIDER", os.getenv("EMBEDDING_PROVIDER", "gemini")).lower()


def _resolve_pdf_path() -> Path:
    raw = (os.getenv("PDF_PATH") or "").strip() or DEFAULT_PDF
    pdf = Path(raw)
    if not pdf.is_absolute():
        pdf = PROJECT_ROOT / pdf
    if not pdf.is_file():
        raise FileNotFoundError(f"PDF não encontrado: {pdf}")
    return pdf


class BatchedEmbeddings(Embeddings):
    """Evita estourar cota gratuita da API ao embedar muitos chunks de uma vez."""

    def __init__(self, wrapped: Embeddings) -> None:
        self.wrapped = wrapped

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        all_vectors: list[list[float]] = []
        total = (len(texts) + EMBED_BATCH_SIZE - 1) // EMBED_BATCH_SIZE

        for i in range(0, len(texts), EMBED_BATCH_SIZE):
            batch_num = i // EMBED_BATCH_SIZE + 1
            batch = texts[i : i + EMBED_BATCH_SIZE]
            if batch_num > 1:
                time.sleep(EMBED_BATCH_DELAY_SEC)
            print(f"  Embedding lote {batch_num}/{total} ({len(batch)} textos)...")
            all_vectors.extend(self._embed_with_retry(batch))

        return all_vectors

    def _embed_with_retry(self, texts: list[str]) -> list[list[float]]:
        while True:
            try:
                return self.wrapped.embed_documents(texts)
            except Exception as exc:
                if not _is_rate_limit(exc):
                    raise
                delay = _retry_delay(exc)
                print(f"Cota da API atingida. Aguardando {delay:.0f}s...")
                time.sleep(delay)

    def embed_query(self, text: str) -> list[float]:
        while True:
            try:
                return self.wrapped.embed_query(text)
            except Exception as exc:
                if not _is_rate_limit(exc):
                    raise
                delay = _retry_delay(exc)
                print(f"Cota da API atingida. Aguardando {delay:.0f}s...")
                time.sleep(delay)


def _is_rate_limit(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "429" in msg or "resource_exhausted" in msg or "quota" in msg


def _retry_delay(exc: Exception) -> float:
    if hasattr(exc, "details") and isinstance(exc.details, dict):
        for item in exc.details.get("error", {}).get("details", []):
            delay = item.get("retryDelay")
            if delay:
                return max(float(str(delay).rstrip("s")), 1.0)
    return 65.0


def get_embeddings() -> Embeddings:
    if PROVIDER == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada. Verifique o arquivo .env")

        from langchain_openai import OpenAIEmbeddings

        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        return BatchedEmbeddings(OpenAIEmbeddings(model=model, api_key=api_key))

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não encontrada. Verifique o arquivo .env")

    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    # embedding-001 foi descontinuado na API atual; gemini-embedding-001 é o sucessor
    model = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    base = GoogleGenerativeAIEmbeddings(model=model, google_api_key=api_key)
    return BatchedEmbeddings(base)


def get_llm():
    if PROVIDER == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada. Verifique o arquivo .env")

        from langchain_openai import ChatOpenAI

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model, api_key=api_key)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não encontrada. Verifique o arquivo .env")

    from langchain_google_genai import ChatGoogleGenerativeAI

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)


def get_vectorstore():
    from langchain_postgres import PGVector

    return PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
    )
