from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.search import FALLBACK_RESPONSE, answer_question


def test_answer_question_returns_fallback_when_context_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "src.search.load_settings",
        lambda: SimpleNamespace(
            database_url="postgresql+psycopg://postgres:postgres@localhost:5432/rag",
            pg_vector_collection_name="rag_document",
            llm_provider="openai",
        ),
    )
    monkeypatch.setattr("src.search.validate_provider_credentials", lambda settings: None)
    monkeypatch.setattr("src.search.get_embeddings_client", lambda settings: object())

    class EmptyVectorStore:
        def similarity_search_with_score(self, question: str, k: int):
            return []

    monkeypatch.setattr(
        "src.search.get_vector_store",
        lambda settings, embeddings: EmptyVectorStore(),
    )
    chat_invocations: list[str] = []
    monkeypatch.setattr(
        "src.search.get_chat_client",
        lambda settings: SimpleNamespace(
            invoke=lambda prompt: chat_invocations.append(prompt) or None
        ),
    )

    result = answer_question("Existe informacao sobre clientes?")

    assert result["answer"] == FALLBACK_RESPONSE
    assert result["documents"] == []
    assert "Existe informacao sobre clientes?" in result["prompt"]
    assert chat_invocations == []
