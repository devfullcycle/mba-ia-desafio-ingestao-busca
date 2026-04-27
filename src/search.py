from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain_core.documents import Document

try:
    from config import ConfigurationError, load_settings, validate_provider_credentials
    from providers import get_chat_client, get_embeddings_client
    from vectorstore import get_vector_store
except ImportError:  # pragma: no cover - fallback for package imports
    from src.config import ConfigurationError, load_settings, validate_provider_credentials
    from src.providers import get_chat_client, get_embeddings_client
    from src.vectorstore import get_vector_store

FALLBACK_RESPONSE = "Nao tenho informacoes necessarias para responder sua pergunta."
PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informacao nao estiver explicitamente no CONTEXTO, responda:
  "{fallback}"
- Nunca invente ou use conhecimento externo.
- Nunca produza opinioes ou interpretacoes alem do que esta escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual e a capital da Franca?"
Resposta: "{fallback}"

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "{fallback}"

Pergunta: "Voce acha isso bom ou ruim?"
Resposta: "{fallback}"

PERGUNTA DO USUARIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUARIO"
"""


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    score: float
    metadata: dict[str, Any]


class SearchServiceError(RuntimeError):
    """Raised when semantic search cannot complete."""


def normalize_search_results(
    search_results: list[tuple[Document, float]],
) -> list[RetrievedChunk]:
    normalized = []
    for document, score in search_results:
        normalized.append(
            RetrievedChunk(
                content=document.page_content.strip(),
                score=float(score),
                metadata=dict(document.metadata),
            )
        )
    return normalized


def build_context(chunks: list[RetrievedChunk]) -> str:
    context_parts = []
    for index, chunk in enumerate(chunks, start=1):
        if not chunk.content:
            continue
        context_parts.append(f"[Trecho {index}]\n{chunk.content}")
    return "\n\n".join(context_parts)


def search_prompt(question: str | None = None, contexto: str = "") -> str:
    return PROMPT_TEMPLATE.format(
        contexto=contexto.strip(),
        pergunta=(question or "").strip(),
        fallback=FALLBACK_RESPONSE,
    )


def answer_question(question: str) -> dict[str, Any]:
    settings = load_settings()
    validate_provider_credentials(settings)

    embeddings = get_embeddings_client(settings)
    vector_store = get_vector_store(settings, embeddings)

    try:
        raw_results = vector_store.similarity_search_with_score(question, k=10)
    except Exception as exc:  # pragma: no cover - third-party/database behavior
        raise SearchServiceError(
            "Falha ao consultar documentos no PostgreSQL com pgvector."
        ) from exc

    chunks = normalize_search_results(raw_results)
    context = build_context(chunks)

    if not context:
        return {
            "answer": FALLBACK_RESPONSE,
            "documents": chunks,
            "prompt": search_prompt(question, contexto=""),
        }

    chat_client = get_chat_client(settings)
    prompt = search_prompt(question, contexto=context)

    try:
        response = chat_client.invoke(prompt)
    except Exception as exc:  # pragma: no cover - provider behavior
        raise SearchServiceError("Falha ao gerar resposta com o provedor de chat.") from exc

    answer = getattr(response, "content", str(response)).strip() or FALLBACK_RESPONSE
    return {
        "answer": answer,
        "documents": chunks,
        "prompt": prompt,
    }


if __name__ == "__main__":
    try:
        raise SystemExit("Use este modulo via src/chat.py.")
    except ConfigurationError as exc:
        print(exc)
        raise SystemExit(1) from exc
