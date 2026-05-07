import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

for k in ("GOOGLE_API_KEY", "GOOGLE_EMBEDDING_MODEL", "PGVECTOR_URL","PGVECTOR_COLLECTION", "PDF_PATH"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")
    
PDF_PATH = os.getenv("PDF_PATH")

docs = PyPDFLoader(str(PDF_PATH)).load()

splits = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=150, add_start_index=False).split_documents(docs)
if not splits:
    raise SystemExit(0)

def ingest_pdf():
     # Criar embeddings com Gemini
    embeddings = GoogleGenerativeAIEmbeddings(model=os.getenv("GOOGLE_EMBEDDING_MODEL"))

    print("PGVECTOR_URL:", os.getenv("PGVECTOR_URL"))
    print("PGVECTOR_COLLECTION:", os.getenv("PGVECTOR_COLLECTION"))
    print("embeddings defined:", 'embeddings' in globals() or 'embeddings' in locals())
    print("type(embeddings):", type(embeddings) if 'embeddings' in globals() or 'embeddings' in locals() else None)
    # Conectar ao Postgres/pgvector
    vector_store = PGVector(
        connection=os.getenv("PGVECTOR_URL"),
        collection_name=os.getenv("PGVECTOR_COLLECTION"),
        embeddings=embeddings,
    )

    # Inserir documentos no banco
    vector_store.add_documents(splits)
    print(f"Ingestão concluída: {len(splits)} chunks gravados em {os.getenv('PGVECTOR_COLLECTION')}")


if __name__ == "__main__":
    ingest_pdf()