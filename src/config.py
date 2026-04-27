from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

SUPPORTED_PROVIDERS = {"openai", "gemini"}


class ConfigurationError(ValueError):
    """Raised when a required environment variable is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    database_url: str
    pg_vector_collection_name: str
    pdf_path: str
    llm_provider: str
    openai_api_key: Optional[str]
    openai_embedding_model: str
    openai_chat_model: str
    google_api_key: Optional[str]
    google_embedding_model: str
    google_chat_model: str
    debug_retrieved_chunks: bool


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name, default)
    if value is None:
        return None

    value = value.strip()
    if not value:
        return None

    return value


def _require_env(name: str, default: Optional[str] = None) -> str:
    value = _get_env(name, default)
    if value is None:
        raise ConfigurationError(f"Variavel de ambiente obrigatoria ausente: {name}")
    return value


def load_settings() -> Settings:
    llm_provider = _require_env("LLM_PROVIDER", "openai").lower()
    if llm_provider not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise ConfigurationError(
            f"Valor invalido para LLM_PROVIDER: {llm_provider}. Use um de: {supported}"
        )

    return Settings(
        database_url=_require_env("DATABASE_URL"),
        pg_vector_collection_name=_require_env("PG_VECTOR_COLLECTION_NAME"),
        pdf_path=_require_env("PDF_PATH", "document.pdf"),
        llm_provider=llm_provider,
        openai_api_key=_get_env("OPENAI_API_KEY"),
        openai_embedding_model=_require_env(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        ),
        openai_chat_model=_require_env("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        google_api_key=_get_env("GOOGLE_API_KEY"),
        google_embedding_model=_require_env(
            "GOOGLE_EMBEDDING_MODEL", "models/embedding-001"
        ),
        google_chat_model=_require_env("GOOGLE_CHAT_MODEL", "gemini-1.5-flash"),
        debug_retrieved_chunks=_get_env("DEBUG_RETRIEVED_CHUNKS", "false") == "true",
    )


def validate_provider_credentials(settings: Settings) -> None:
    if settings.llm_provider == "openai" and not settings.openai_api_key:
        raise ConfigurationError(
            "Variavel de ambiente obrigatoria ausente para o provedor OpenAI: OPENAI_API_KEY"
        )

    if settings.llm_provider == "gemini" and not settings.google_api_key:
        raise ConfigurationError(
            "Variavel de ambiente obrigatoria ausente para o provedor Gemini: GOOGLE_API_KEY"
        )
