from __future__ import annotations

from src.search import FALLBACK_RESPONSE, search_prompt


def test_search_prompt_includes_context_rules_and_question() -> None:
    prompt = search_prompt(
        "O que o documento fala sobre pgvector?",
        contexto="[Trecho 1]\npgvector permite busca vetorial no PostgreSQL.",
    )

    assert "CONTEXTO:" in prompt
    assert "[Trecho 1]\npgvector permite busca vetorial no PostgreSQL." in prompt
    assert "Responda somente com base no CONTEXTO." in prompt
    assert FALLBACK_RESPONSE in prompt
    assert "O que o documento fala sobre pgvector?" in prompt
