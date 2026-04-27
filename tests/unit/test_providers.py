from __future__ import annotations

import pytest
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config import load_settings
from src.providers import get_chat_client, get_embeddings_client


def test_openai_provider_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    )
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    monkeypatch.setenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    settings = load_settings()

    embeddings_client = get_embeddings_client(settings)
    chat_client = get_chat_client(settings)

    assert isinstance(embeddings_client, OpenAIEmbeddings)
    assert isinstance(chat_client, ChatOpenAI)


def test_gemini_provider_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    )
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    monkeypatch.setenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
    monkeypatch.setenv("GOOGLE_CHAT_MODEL", "gemini-1.5-flash")

    settings = load_settings()

    embeddings_client = get_embeddings_client(settings)
    chat_client = get_chat_client(settings)

    assert isinstance(embeddings_client, GoogleGenerativeAIEmbeddings)
    assert isinstance(chat_client, ChatGoogleGenerativeAI)
