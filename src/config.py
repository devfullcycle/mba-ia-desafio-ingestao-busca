from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    google_api_key: str
    google_embedding_model: str = "gemini-embedding-001"
    google_llm_model: str = "gemini-flash-lite-latest"
    database_url: str
    pg_vector_collection_name: str
    pdf_path: str


def get_settings() -> Settings:
    return Settings()
