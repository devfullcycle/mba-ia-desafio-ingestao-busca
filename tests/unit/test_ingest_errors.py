from __future__ import annotations

import pytest
from langchain_core.documents import Document

from src.config import ConfigurationError
from src.ingest import IngestionError, ingest_pdf, load_pdf_documents, persist_chunks


def test_load_pdf_documents_fails_for_missing_file() -> None:
    with pytest.raises(IngestionError, match="Arquivo PDF nao encontrado"):
        load_pdf_documents("missing-document.pdf")


def test_ingest_pdf_surfaces_missing_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "rag_document")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    with pytest.raises(
        ConfigurationError,
        match="Variavel de ambiente obrigatoria ausente: DATABASE_URL",
    ):
        ingest_pdf()


def test_persist_chunks_surfaces_storage_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSettings:
        pass

    chunks = [Document(page_content="chunk", metadata={"page": 1})]

    monkeypatch.setattr("src.ingest.get_embeddings_client", lambda settings: object())

    class BrokenVectorStore:
        def add_documents(self, docs, ids=None):
            raise RuntimeError("db down")

    monkeypatch.setattr(
        "src.ingest.get_vector_store",
        lambda settings, embeddings: BrokenVectorStore(),
    )

    with pytest.raises(
        IngestionError,
        match="Falha ao persistir os chunks no PostgreSQL com pgvector.",
    ):
        persist_chunks(FakeSettings(), chunks)
