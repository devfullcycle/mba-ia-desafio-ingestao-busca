import os

from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")


def create_embeddings():
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def create_vector_store(embeddings):
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL
    )
