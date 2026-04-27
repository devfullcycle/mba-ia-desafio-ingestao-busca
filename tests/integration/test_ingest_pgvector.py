from __future__ import annotations

import os
import uuid

import psycopg
import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.config import load_settings
from src.ingest import persist_chunks
from src.vectorstore import get_vector_store


class FakeEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        size = float(len(text))
        checksum = float(sum(ord(char) for char in text) % 1000)
        return [size, checksum, 1.0]


def _is_database_available(database_url: str) -> bool:
    try:
        with psycopg.connect(database_url, connect_timeout=2):
            return True
    except Exception:
        return False


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL nao configurada para teste de integracao.",
)
def test_ingest_persists_documents_in_pgvector(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = load_settings()

    if not _is_database_available(settings.database_url):
        pytest.skip("PostgreSQL nao esta acessivel para o teste de integracao.")

    collection_name = f"test_ingest_{uuid.uuid4().hex}"
    chunks = [
        Document(page_content="LangChain com pgvector", metadata={"page": 1}),
        Document(page_content="Busca semantica em PostgreSQL", metadata={"page": 2}),
    ]

    monkeypatch.setattr("src.ingest.get_embeddings_client", lambda settings: FakeEmbeddings())
    monkeypatch.setattr(
        "src.ingest.get_vector_store",
        lambda settings, embeddings: get_vector_store(
            settings,
            embeddings,
            collection_name=collection_name,
            pre_delete_collection=True,
        ),
    )

    result = persist_chunks(settings, chunks)
    vector_store = get_vector_store(
        settings,
        FakeEmbeddings(),
        collection_name=collection_name,
    )

    stored = vector_store.similarity_search_with_score("pgvector", k=10)

    assert result["stored_chunks"] == 2
    assert len(stored) == 2
    assert {doc.metadata["page"] for doc, _score in stored} == {1, 2}

    vector_store.delete_collection()
