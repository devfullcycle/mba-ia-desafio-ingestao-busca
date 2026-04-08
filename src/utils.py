from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

from config import Config


def validate_chunks(chunks: list[Document]) -> None:
    """Valida se a lista de chunks não está vazia.

    Args:
        chunks: Lista de documentos (chunks) a serem validados.

    Raises:
        ValueError: Se a lista de chunks estiver vazia.
    """
    if not chunks:
        raise ValueError("A lista de chunks não pode estar vazia. Verifique o arquivo PDF.")
    

def create_embeddings():
    match Config.EMBEDDING_MODEL:
        case "open_ai":
            return OpenAIEmbeddings(model=Config.get_embedding_model_name())
        case "google":
            return GoogleGenerativeAIEmbeddings(model=Config.get_embedding_model_name())
        case _:
            raise LookupError("Opção de embedding model inválida.")

def create_vector_store() -> PGVector:
    return PGVector(
        embeddings=create_embeddings(),
        collection_name=Config.get_collection_name(),
        connection=Config.PGVECTOR_URL,
        use_jsonb=True
    )