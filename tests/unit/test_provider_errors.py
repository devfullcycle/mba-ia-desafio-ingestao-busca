from __future__ import annotations

import pytest

from src.config import ConfigurationError, load_settings
from src.providers import get_chat_client, get_embeddings_client


def test_openai_provider_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    )
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = load_settings()

    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        get_embeddings_client(settings)


def test_gemini_provider_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    )
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    settings = load_settings()

    with pytest.raises(ConfigurationError, match="GOOGLE_API_KEY"):
        get_chat_client(settings)


def test_invalid_provider_fails_during_settings_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    )
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")
    monkeypatch.setenv("LLM_PROVIDER", "claude")

    with pytest.raises(ConfigurationError, match="Valor invalido para LLM_PROVIDER"):
        load_settings()
