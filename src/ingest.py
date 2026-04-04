import os
from pathlib import Path
from utils import validate_chunks, resolve_path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv
load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))


def create_loader(path: Path) -> PyPDFLoader:
    return PyPDFLoader(str(path))

def create_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=False
    )

def enrich_documents(chunks:list[Document]) -> list[Document]:
    extractor = lambda docs: {
        k: v for k,v in docs.metadata.items() 
        if v not in ("",None)
    }
    return [Document(page_content=c.page_content, metadata=extractor(c)) for c in chunks]

def ingest_pdf():
    path = resolve_path()
    pdf_loader = create_loader(path)
    
    chunks = create_text_splitter().split_documents(
            pdf_loader.load()
    )
    validate_chunks(chunks)
    chunks = enrich_documents(chunks=chunks)
    print("OK")


if __name__ == "__main__":
    ingest_pdf()