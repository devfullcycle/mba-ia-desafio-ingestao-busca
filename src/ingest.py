import time
from pathlib import Path

from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import load_get_config
from vector_store import get_vector_store

PROJECT_ROOT = Path(__file__).resolve().parents[1]
config = load_get_config()

EMBED_BATCH_SIZE = 90
EMBED_BATCH_INTERVAL_SECONDS = 61


def get_pdf_docs_chunks(pdf_name: str) -> list[Document]:
    file_path = Path(PROJECT_ROOT) / pdf_name
    if not file_path.is_file():
        return []

    docs = PyPDFLoader(file_path).load()
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150
    ).split_documents(docs)

    return [
        Document(
            id=f"{config.pgvector_collection}-{i}",
            page_content=c.page_content,
            metadata={k: v for k, v in c.metadata.items()
                      if v not in ('', None, [], (), {})}
        ) for i, c in enumerate(chunks)
    ]


def ingest_pdf(pdf_name: str) -> None:
    docs_chunks = get_pdf_docs_chunks(pdf_name)
    if not docs_chunks:
        return

    vector_store = get_vector_store()

    # Add documents in steps due to Gemini free tier rate limits
    for start in range(0, len(docs_chunks), EMBED_BATCH_SIZE):
        if start:
            time.sleep(EMBED_BATCH_INTERVAL_SECONDS)
        vector_store.add_documents(docs_chunks[start:start + EMBED_BATCH_SIZE])
