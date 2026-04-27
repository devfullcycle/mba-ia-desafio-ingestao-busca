from __future__ import annotations

from langchain_core.documents import Document

from src.ingest import split_documents


def test_split_documents_uses_fixed_chunk_size_and_overlap() -> None:
    document = Document(
        page_content="A" * 2200,
        metadata={"page": 1, "source": "document.pdf"},
    )

    chunks = split_documents([document])

    assert len(chunks) >= 3
    assert all(len(chunk.page_content) <= 1000 for chunk in chunks)
    assert chunks[0].page_content[-150:] == chunks[1].page_content[:150]
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[1].metadata["chunk_index"] == 1
