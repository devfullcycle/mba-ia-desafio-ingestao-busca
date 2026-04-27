"""Provider factories for embeddings and chat models."""

from __future__ import annotations

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

try:
    from config import ConfigurationError, Settings, validate_provider_credentials
except ImportError:  # pragma: no cover - fallback for package imports
    from src.config import ConfigurationError, Settings, validate_provider_credentials


def _ensure_supported_provider(settings: Settings) -> None:
    if settings.llm_provider not in {"openai", "gemini"}:
        raise ConfigurationError(
            f"Valor invalido para LLM_PROVIDER: {settings.llm_provider}. "
            "Use um de: gemini, openai"
        )


def get_embeddings_client(settings: Settings) -> object:
    validate_provider_credentials(settings)
    _ensure_supported_provider(settings)

    if settings.llm_provider == "openai":
        return OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )

    return GoogleGenerativeAIEmbeddings(
        google_api_key=settings.google_api_key,
        model=settings.google_embedding_model,
    )


def get_chat_client(settings: Settings) -> object:
    validate_provider_credentials(settings)
    _ensure_supported_provider(settings)

    if settings.llm_provider == "openai":
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_chat_model,
        )

    return ChatGoogleGenerativeAI(
        google_api_key=settings.google_api_key,
        model=settings.google_chat_model,
    )
