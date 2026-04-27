from pathlib import Path
from uuid import uuid4

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from config import ConfigurationError, load_settings, validate_provider_credentials
    from providers import get_embeddings_client
    from vectorstore import get_vector_store
except ImportError:  # pragma: no cover - fallback for package imports
    from src.config import ConfigurationError, load_settings, validate_provider_credentials
    from src.providers import get_embeddings_client
    from src.vectorstore import get_vector_store


class IngestionError(RuntimeError):
    """Raised when the ingestion pipeline cannot complete."""


def load_pdf_documents(pdf_path: str) -> list[Document]:
    path = Path(pdf_path)
    if not path.exists():
        raise IngestionError(f"Arquivo PDF nao encontrado em: {pdf_path}")

    try:
        loader = PyPDFLoader(str(path))
        return loader.load()
    except Exception as exc:  # pragma: no cover - third-party loader behavior
        raise IngestionError(f"Falha ao ler o PDF informado: {pdf_path}") from exc


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        metadata = dict(chunk.metadata)
        metadata["chunk_index"] = index
        chunk.metadata = metadata

    return chunks


def build_document_ids(chunks: list[Document]) -> list[str]:
    return [str(uuid4()) for _ in chunks]


def persist_chunks(settings, chunks: list[Document]) -> dict[str, int]:
    embeddings = get_embeddings_client(settings)
    vector_store = get_vector_store(settings, embeddings)
    ids = build_document_ids(chunks)

    try:
        stored_ids = vector_store.add_documents(chunks, ids=ids)
    except Exception as exc:  # pragma: no cover - database/client behavior
        raise IngestionError(
            "Falha ao persistir os chunks no PostgreSQL com pgvector."
        ) from exc

    return {"stored_chunks": len(stored_ids)}


def ingest_pdf():
    settings = load_settings()
    validate_provider_credentials(settings)
    documents = load_pdf_documents(settings.pdf_path)
    chunks = split_documents(documents)
    persistence = persist_chunks(settings, chunks)

    return {
        "pages": len(documents),
        "chunks": len(chunks),
        **persistence,
    }


if __name__ == "__main__":
    try:
        result = ingest_pdf()
        print(
            f"Ingestao concluida com sucesso: {result['pages']} paginas e "
            f"{result['stored_chunks']} chunks persistidos."
        )
    except (ConfigurationError, IngestionError) as exc:
        print(exc)
        raise SystemExit(1) from exc
