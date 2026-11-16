from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / '.env')
    api_key: str
    llm_model: str
    embedding_model: str
    pgvector_url: str
    pgvector_collection: str


@lru_cache
def load_get_config() -> Settings:
    # Fields are filled from env/.env at runtime; Pylance can't see that.
    return Settings()   # pyright: ignore[reportCallIssue]
