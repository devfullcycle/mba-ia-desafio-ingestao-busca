from __future__ import annotations

from types import SimpleNamespace

import pytest
from langchain_core.documents import Document

from src.chat import main
from src.ingest import ingest_pdf
from src.search import FALLBACK_RESPONSE


def test_cli_flow_runs_ingest_then_answers_and_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "src.ingest.load_settings",
        lambda: SimpleNamespace(pdf_path="document.pdf"),
    )
    monkeypatch.setattr("src.ingest.validate_provider_credentials", lambda settings: None)
    monkeypatch.setattr(
        "src.ingest.load_pdf_documents",
        lambda pdf_path: [
            Document(page_content="pgvector armazena embeddings.", metadata={"page": 1})
        ],
    )
    monkeypatch.setattr(
        "src.ingest.split_documents",
        lambda documents: documents,
    )
    monkeypatch.setattr(
        "src.ingest.persist_chunks",
        lambda settings, chunks: {"stored_chunks": len(chunks)},
    )

    ingestion_result = ingest_pdf()

    monkeypatch.setattr(
        "src.chat.load_settings",
        lambda: SimpleNamespace(debug_retrieved_chunks=False),
    )
    monkeypatch.setattr("src.chat.validate_provider_credentials", lambda settings: None)

    def fake_answer_question(question: str) -> dict[str, object]:
        if "pgvector" in question.lower():
            return {
                "answer": "pgvector armazena embeddings.",
                "documents": [],
            }
        return {
            "answer": FALLBACK_RESPONSE,
            "documents": [],
        }

    monkeypatch.setattr("src.chat.answer_question", fake_answer_question)

    answers = iter(
        [
            "O que o documento diz sobre pgvector?",
            "Qual e a capital da Franca?",
            "",
        ]
    )
    outputs: list[str] = []
    exit_code = main(
        input_func=lambda prompt: next(answers),
        print_func=outputs.append,
    )

    assert ingestion_result == {"pages": 1, "chunks": 1, "stored_chunks": 1}
    assert exit_code == 0
    assert outputs == [
        "RESPOSTA: pgvector armazena embeddings.",
        f"RESPOSTA: {FALLBACK_RESPONSE}",
        "Encerrando chat.",
    ]
