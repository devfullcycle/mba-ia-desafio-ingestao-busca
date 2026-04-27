"""Provider factory placeholder for upcoming SI-01.2."""

from __future__ import annotations

try:
    from config import Settings
except ImportError:  # pragma: no cover - fallback for package imports
    from src.config import Settings


def get_embeddings_client(settings: Settings) -> object:
    raise NotImplementedError(
        "A factory de embeddings sera implementada na SI-01.2."
    )


def get_chat_client(settings: Settings) -> object:
    raise NotImplementedError("A factory de chat sera implementada na SI-01.2.")
