import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centraliza todas as configurações."""

    # Configurações de chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Configurações de banco de dados
    PGVECTOR_URL: str = os.environ["PGVECTOR_URL"]
    PG_VECTOR_COLLECTION_NAME: str = os.environ["PG_VECTOR_COLLECTION_NAME"]

    # Configurações de embedding
    EMBEDDING_MODEL: str = os.environ["EMBEDDING_MODEL"]
    OPENAI_EMBEDDING_MODEL: str = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    GOOGLE_EMBEDDING_MODEL: str = os.environ.get("GOOGLE_EMBEDDING_MODEL", "")

    # Configurações de arquivo
    PDF_PATH: str = os.getenv("PDF_PATH", "")

    @staticmethod
    def get_embedding_model_name() -> str:
        """Retorna o nome do modelo de embedding baseado na configuração."""
        match Config.EMBEDDING_MODEL:
            case "open_ai":
                return Config.OPENAI_EMBEDDING_MODEL
            case "google":
                return Config.GOOGLE_EMBEDDING_MODEL
            case _:
                raise LookupError(f"Embedding model not found: {Config.EMBEDDING_MODEL}")

    @staticmethod
    def get_collection_name() -> str:
        """Retorna o nome da coleção formatado com o modelo de embedding."""
        model_name = Config.get_embedding_model_name().replace('/', '_')
        return f"{Config.PG_VECTOR_COLLECTION_NAME}_{model_name}"

    @staticmethod
    def get_pdf_path() -> Path:
        """Resolve e valida o caminho do PDF."""
        user_path = Path(Config.PDF_PATH)

        if not user_path.is_absolute():
            user_path = user_path.resolve()

        if not user_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {user_path}")

        return user_path

    @staticmethod
    def validate() -> None:
        """Valida se todas as configurações obrigatórias estão presentes."""
        required_vars = [
            "PGVECTOR_URL",
            "PG_VECTOR_COLLECTION_NAME",
            "EMBEDDING_MODEL",
            "PDF_PATH"
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise EnvironmentError(
                f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing_vars)}"
            )
