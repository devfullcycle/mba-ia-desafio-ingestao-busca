import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from utils import AdditionalMetadata, resolve_path, validate_chunks

load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))
CONNECTION = os.environ["PGVECTOR_URL"]
COLLECTION_BASE_NAME = os.environ["PG_VECTOR_COLLECTION_NAME"]
EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]


def create_loader(path: Path) -> PyPDFLoader:
    return PyPDFLoader(str(path))

def create_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=False
    )

def get_embedding_model() -> str:
    match EMBEDDING_MODEL:
        case "open_ai":
            return os.environ["OPENAI_EMBEDDING_MODEL"]
        case "google":
            return os.environ["GOOGLE_EMBEDDING_MODEL"]
        case _:
            raise LookupError("Embedding model not found: {EMBEDDING_MODEL}") 

def enrich_documents(chunks: list[Document]) -> list[Document]:

    for i in range(len(chunks)):
        chunks[i].metadata["embedding_type"] = get_embedding_model() 

    def extract_metadata(doc:Document):
        return {
            k: v for k, v in doc.metadata.items()
            if v not in ("", None)
        }

    return [Document(page_content=c.page_content, metadata=extract_metadata(c)) for c in chunks]

def create_embeddings():
    return OpenAIEmbeddings(model=get_embedding_model())

def create_vector_store() -> PGVector:
    collection_name = f"{COLLECTION_BASE_NAME}_{get_embedding_model().replace('/', '_')}"
    
    return PGVector(
        embeddings=create_embeddings(),
        collection_name=collection_name,
        connection=CONNECTION,
        use_jsonb=True
    )


def ingest_pdf():
    path = resolve_path()
    pdf_loader = create_loader(path)
    
    chunks = create_text_splitter().split_documents(
            pdf_loader.load()
    )
    validate_chunks(chunks)

    chunks = enrich_documents(chunks=chunks)
    vector_store = create_vector_store()

    print("OK")
    
if __name__ == "__main__":
    ingest_pdf()