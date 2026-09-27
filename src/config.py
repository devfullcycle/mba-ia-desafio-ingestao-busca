from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    google_api_key: str = Field(min_length=1)
    google_embedding_model: str = "gemini-embedding-001"
    google_llm_model: str = "gemini-flash-lite-latest"
    database_url: str = Field(min_length=1)
    pg_vector_collection_name: str = Field(min_length=1)
    pdf_path: str = Field(min_length=1)


def get_settings() -> Settings:
    return Settings()
