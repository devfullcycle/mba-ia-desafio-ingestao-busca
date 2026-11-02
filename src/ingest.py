# src/ingest.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 1) Carregadores/split/embeddings/vectorstore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_postgres import PGVector


def _get_embeddings():
    load_dotenv()
    provider = (os.getenv("EMBEDDING_PROVIDER") or "").lower()
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if provider == "local":
        model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        return HuggingFaceEmbeddings(model_name=model_name)

    if provider == "gemini":
        if not google_key:
            raise RuntimeError("GOOGLE_API_KEY ausente para provider gemini")
        model = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
        return GoogleGenerativeAIEmbeddings(model=model, google_api_key=google_key)

    if openai_key:
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        return OpenAIEmbeddings(model=model, api_key=openai_key)

    if google_key:
        model = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
        return GoogleGenerativeAIEmbeddings(model=model, google_api_key=google_key)

    model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name=model_name)


def main():
    load_dotenv()

    # 1) Ler configurações essenciais
    pdf_path = os.getenv("PDF_PATH", "./document.pdf")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF não encontrado em: {pdf_path}")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não definido no .env")

    collection = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")

    # 2) Criar a engine do SQLAlchemy
    engine = create_engine(database_url)

    # 3) Carregar PDF (cada página vira um Document)
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    print(f"[ingest] Páginas carregadas: {len(docs)}")

    # 4) Split em chunks 1000/150 (requisito do desafio)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    print(f"[ingest] Chunks gerados: {len(chunks)}")

    # 5) Embeddings (OpenAI ou Gemini)
    embeddings = _get_embeddings()

    # 6) Persistir no Postgres/pgvector usando a factory (cria/usa a coleção)
    print("[ingest] Gravando embeddings no Postgres...")
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,        # <- parâmetro correto nas versões atuais
        connection=engine,           # <- engine SQLAlchemy
        collection_name=collection,  # <- ex.: 'pdf_chunks'
        use_jsonb=True,              # metadados ficam em JSONB
    )

    print("[ingest] Concluído! ✅")


if __name__ == "__main__":
    main()
