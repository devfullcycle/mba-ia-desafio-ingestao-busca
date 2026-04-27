"""PGVector helpers."""

from __future__ import annotations

from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector

try:
    from config import Settings
except ImportError:  # pragma: no cover - fallback for package imports
    from src.config import Settings


def get_vector_store(
    settings: Settings,
    embeddings: Embeddings,
    *,
    collection_name: Optional[str] = None,
    pre_delete_collection: bool = False,
) -> PGVector:
    return PGVector(
        embeddings=embeddings,
        connection=settings.database_url,
        collection_name=collection_name or settings.pg_vector_collection_name,
        use_jsonb=True,
        create_extension=True,
        pre_delete_collection=pre_delete_collection,
    )
