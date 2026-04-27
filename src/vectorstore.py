"""PGVector wrapper placeholder for upcoming SI-01.3."""

from __future__ import annotations

try:
    from config import Settings
except ImportError:  # pragma: no cover - fallback for package imports
    from src.config import Settings


def get_vector_store(settings: Settings) -> object:
    raise NotImplementedError("O wrapper de PGVector sera implementado na SI-01.3.")
