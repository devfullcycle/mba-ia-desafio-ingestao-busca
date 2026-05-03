import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH") or "document.pdf"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")

def get_embeddings():
    if os.getenv("OPENAI_API_KEY"):
        print("Using OpenAI Embeddings")
        return OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))
    elif os.getenv("GOOGLE_API_KEY"):
        print("Using Google Generative AI Embeddings")
        return GoogleGenerativeAIEmbeddings(model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001"))
    else:
        raise ValueError("Neither OPENAI_API_KEY nor GOOGLE_API_KEY found in environment. Please set one of them in your .env file.")

import time

def ingest_pdf():
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF file not found at {PDF_PATH}")
        return

    print(f"Starting ingestion for: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages from {PDF_PATH}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    try:
        embeddings = get_embeddings()
        
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            connection=DATABASE_URL,
            use_jsonb=True,
        )

        print(f"Adding {len(chunks)} chunks to pgVector (database: {DATABASE_URL}, collection: {COLLECTION_NAME})...")
        
        batch_size = 5
        delay = 10
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            vector_store.add_documents(batch)
            print(f"Progress: {min(i + batch_size, len(chunks))}/{len(chunks)} chunks added.")
            
            if i + batch_size < len(chunks):
                print(f"Waiting {delay} seconds to avoid rate limits...")
                time.sleep(delay)
                
        print("Successfully ingested all chunks into the database.")
        
    except Exception as e:
        print(f"An error occurred during ingestion: {e}")


if __name__ == "__main__":
    ingest_pdf()