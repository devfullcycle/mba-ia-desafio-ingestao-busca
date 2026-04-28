import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
load_dotenv()

PDF_PATH = "./document.pdf"

def ingest_pdf():
    chunks = get_chunks()
    enriched_chunks = enrich_chunks(chunks)
    persist_chunks(enriched_chunks)

def get_chunks():
    document = PyPDFLoader(PDF_PATH)
    pdfData = document.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(pdfData)
    return chunks

def enrich_chunks(chunks):
    enriched = []
    for i, chunk in enumerate(chunks):
        meta = {**chunk.metadata, "id": f"doc-{i}"}
        enriched.append(Document(
            page_content=chunk.page_content,
            metadata=meta,
        ))
    return enriched    

def persist_chunks(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION"),
        connection=os.getenv("PGVECTOR_URL"),
        use_jsonb=True,
    )
    ids = [c.metadata["id"] for c in chunks]
    store.add_documents(documents=chunks, ids=ids)

if __name__ == "__main__":
    ingest_pdf()