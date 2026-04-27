from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.chat import main
from src.config import ConfigurationError


def test_chat_cli_exits_on_empty_question(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.chat.load_settings",
        lambda: SimpleNamespace(debug_retrieved_chunks=False),
    )
    monkeypatch.setattr("src.chat.validate_provider_credentials", lambda settings: None)

    outputs: list[str] = []
    exit_code = main(
        input_func=lambda prompt: "",
        print_func=outputs.append,
    )

    assert exit_code == 0
    assert outputs == ["Encerrando chat."]


def test_chat_cli_surfaces_initialization_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "src.chat.load_settings",
        lambda: SimpleNamespace(debug_retrieved_chunks=False),
    )
    monkeypatch.setattr("src.chat.validate_provider_credentials", lambda settings: None)
    monkeypatch.setattr(
        "src.chat.answer_question",
        lambda question: (_ for _ in ()).throw(ConfigurationError("Falha de inicializacao")),
    )

    outputs: list[str] = []
    exit_code = main(
        input_func=lambda prompt: "Como funciona?",
        print_func=outputs.append,
    )

    assert exit_code == 1
    assert outputs == ["Nao foi possivel responder a pergunta. Falha de inicializacao"]


def test_chat_cli_formats_basic_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.chat.load_settings",
        lambda: SimpleNamespace(debug_retrieved_chunks=False),
    )
    monkeypatch.setattr("src.chat.validate_provider_credentials", lambda settings: None)
    monkeypatch.setattr(
        "src.chat.answer_question",
        lambda question: {
            "answer": "Resposta contextual.",
            "documents": [],
        },
    )

    answers = iter(["O que existe no documento?", ""])
    outputs: list[str] = []
    exit_code = main(
        input_func=lambda prompt: next(answers),
        print_func=outputs.append,
    )

    assert exit_code == 0
    assert outputs == ["RESPOSTA: Resposta contextual.", "Encerrando chat."]
