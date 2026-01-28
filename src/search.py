import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

def get_vectorstore():
    load_dotenv()

    pg_url = os.getenv("PGVECTOR_URL")
    collection = os.getenv("PGVECTOR_COLLECTION", "default_collection")
    embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")

    if not pg_url:
        raise RuntimeError("PGVECTOR_URL não encontrada no .env")

    embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)

    return PGVector(
        connection=pg_url,
        embeddings=embeddings,
        collection_name=collection,
        use_jsonb=True,
    )

def similarity_search(query: str, k: int = 10):
    vs = get_vectorstore()
    return vs.similarity_search_with_score(query, k=k)
