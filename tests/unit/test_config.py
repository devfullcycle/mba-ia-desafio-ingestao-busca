from __future__ import annotations

import pytest

from src.config import ConfigurationError, load_settings, validate_provider_credentials


def test_load_settings_reads_defaults_and_required_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag")
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("PDF_PATH", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("DEBUG_RETRIEVED_CHUNKS", raising=False)

    settings = load_settings()

    assert settings.llm_provider == "openai"
    assert settings.pdf_path == "document.pdf"
    assert settings.openai_chat_model == "gpt-4o-mini"
    assert settings.debug_retrieved_chunks is False


def test_load_settings_requires_environment_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")

    with pytest.raises(
        ConfigurationError,
        match="Variavel de ambiente obrigatoria ausente: DATABASE_URL",
    ):
        load_settings()


def test_load_settings_rejects_invalid_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag")
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")
    monkeypatch.setenv("LLM_PROVIDER", "invalid")

    with pytest.raises(
        ConfigurationError,
        match="Valor invalido para LLM_PROVIDER: invalid",
    ):
        load_settings()


def test_validate_provider_credentials_for_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag")
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = load_settings()

    with pytest.raises(
        ConfigurationError,
        match="OPENAI_API_KEY",
    ):
        validate_provider_credentials(settings)
