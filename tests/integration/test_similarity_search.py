from __future__ import annotations

from types import SimpleNamespace

import pytest
from langchain_core.documents import Document

from src.search import RetrievedChunk, answer_question


def test_answer_question_uses_similarity_search_with_k10_and_builds_context(
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

    captured: dict[str, object] = {}

    class FakeVectorStore:
        def similarity_search_with_score(self, question: str, k: int):
            captured["question"] = question
            captured["k"] = k
            return [
                (
                    Document(
                        page_content="Primeiro trecho relevante sobre pgvector.",
                        metadata={"page": 1, "source": "document.pdf"},
                    ),
                    0.11,
                ),
                (
                    Document(
                        page_content="Segundo trecho com detalhes de busca semantica.",
                        metadata={"page": 2, "source": "document.pdf"},
                    ),
                    0.22,
                ),
            ]

    monkeypatch.setattr(
        "src.search.get_vector_store",
        lambda settings, embeddings: FakeVectorStore(),
    )

    def fake_invoke(prompt: str) -> SimpleNamespace:
        captured["prompt"] = prompt
        return SimpleNamespace(content="Resposta baseada no contexto.")

    monkeypatch.setattr(
        "src.search.get_chat_client",
        lambda settings: SimpleNamespace(invoke=fake_invoke),
    )

    result = answer_question("Como funciona a busca vetorial?")

    assert captured["question"] == "Como funciona a busca vetorial?"
    assert captured["k"] == 10
    assert "Primeiro trecho relevante sobre pgvector." in captured["prompt"]
    assert "Segundo trecho com detalhes de busca semantica." in captured["prompt"]
    assert result["answer"] == "Resposta baseada no contexto."
    assert result["documents"] == [
        RetrievedChunk(
            content="Primeiro trecho relevante sobre pgvector.",
            score=0.11,
            metadata={"page": 1, "source": "document.pdf"},
        ),
        RetrievedChunk(
            content="Segundo trecho com detalhes de busca semantica.",
            score=0.22,
            metadata={"page": 2, "source": "document.pdf"},
        ),
    ]
