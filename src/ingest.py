from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import Config
from utils import validate_chunks, create_vector_store


def create_loader(path: Path) -> PyPDFLoader:
    return PyPDFLoader(str(path))

def create_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        add_start_index=False
    )


def enrich_documents(chunks: list[Document]) -> list[Document]:

    for i in range(len(chunks)):
        chunks[i].metadata["embedding_type"] = Config.get_embedding_model_name()  

    def extract_metadata(doc:Document):
        return {
            k: v for k, v in doc.metadata.items()
            if v not in ("", None)
        }
    return [Document(page_content=c.page_content, metadata=extract_metadata(c)) for c in chunks]


def ingest_pdf():
    path = Config.get_pdf_path()
    pdf_loader = create_loader(path)
    
    chunks = create_text_splitter().split_documents(
            pdf_loader.load()
    )
    validate_chunks(chunks)

    chunks = enrich_documents(chunks=chunks)
    vector_store = create_vector_store()

    ids=[f"{Config.get_embedding_model_name()}-{hash(str(path))}-{i}" for i in range(len(chunks))]
    vector_store.add_documents(
        documents=chunks,
        ids=ids
    )

    
if __name__ == "__main__":
    ingest_pdf()