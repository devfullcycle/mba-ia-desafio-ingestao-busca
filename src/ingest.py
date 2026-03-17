import os
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

def _validate_environment_variables(required_vars: list) -> None:
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(
                f"Missing required environment variable: {var}. "
                f"Please set it in your .env file or environment configuration."
            )

def ingest_pdf() -> None:
    load_dotenv()
        
    required_vars = ["PDF_PATH", "OPENAI_EMBEDDING_MODEL", "PG_VECTOR_COLLECTION_NAME", "DATABASE_URL"]
    _validate_environment_variables(required_vars)
        
    pdf_path = os.getenv("PDF_PATH")
    openapi_embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL")
    collection_name = os.getenv("PG_VECTOR_COLLECTION_NAME")
    database_url = os.getenv("DATABASE_URL")
    
    print("Starting PDF document ingestion...")
    
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()
    print(f"✓ {len(documents)} documents loaded")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=False
    )
    splits = splitter.split_documents(documents)
    
    if not splits:
        raise SystemExit("No documents were processed.")
    
    print(f"✓ {len(splits)} chunks created")
    
    enriched_docs = [
        Document(
            page_content=doc.page_content,
            metadata={k: v for k, v in doc.metadata.items() if v not in ("", None)}
        )
        for doc in splits
    ]
    
    doc_ids = [f"doc-{i}" for i in range(len(enriched_docs))]
    
    embeddings = OpenAIEmbeddings(model=openapi_embedding_model)
    
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=database_url,
        use_jsonb=True
    )
    
    vector_store.add_documents(documents=enriched_docs, ids=doc_ids)
    
    print(f"✓ Ingestion completed successfully! {len(enriched_docs)} documents stored.")

if __name__ == "__main__":
    ingest_pdf()