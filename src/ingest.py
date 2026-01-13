import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

from dotenv import load_dotenv

load_dotenv()

for key in ("PDF_PATH", "GOOGLE_API_KEY", "DATABASE_URL"):
    if not os.getenv(key):
        raise ValueError(f"Environment variable {key} is not set")
    
PDF_PATH = os.getenv("PDF_PATH")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

def enrich_chunks(chunks):
    enriched_chunks = []
    for chunk in chunks:
        enriched_chunk = Document(
            page_content=chunk.page_content,
            metadata={k: v for k, v in chunk.metadata.items() if v not in ("", None)}
        )
        enriched_chunks.append(enriched_chunk)
    return enriched_chunks

def ingest_pdf():
    docs = PyPDFLoader(str(PDF_PATH)).load()
    splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=False).split_documents(docs)
    
    if not splits:
        raise ValueError("No splits found")
    
    enriched_chunks = enrich_chunks(splits)
    
    return enriched_chunks

if __name__ == "__main__":
    chunks = ingest_pdf()
    print(f"Found {len(chunks)} chunks")
    print(chunks[0].page_content)
    print(chunks[0].metadata)
    print("-" * 100)