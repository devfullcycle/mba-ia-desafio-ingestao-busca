import pytest
from pydantic import ValidationError

from config import Settings


def test_settings_uses_default_models_when_not_overridden(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    )
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "test_collection")
    monkeypatch.setenv("PDF_PATH", "document.pdf")
    monkeypatch.delenv("GOOGLE_EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("GOOGLE_LLM_MODEL", raising=False)

    settings = Settings(_env_file=None)

    assert settings.google_embedding_model == "gemini-embedding-001"
    assert settings.google_llm_model == "gemini-flash-lite-latest"


def test_settings_reads_overridden_models(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    monkeypatch.setenv("GOOGLE_EMBEDDING_MODEL", "custom-embedding")
    monkeypatch.setenv("GOOGLE_LLM_MODEL", "custom-llm")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    )
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "test_collection")
    monkeypatch.setenv("PDF_PATH", "document.pdf")

    settings = Settings(_env_file=None)

    assert settings.google_embedding_model == "custom-embedding"
    assert settings.google_llm_model == "custom-llm"


def test_settings_raises_when_required_var_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PG_VECTOR_COLLECTION_NAME", raising=False)
    monkeypatch.delenv("PDF_PATH", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
