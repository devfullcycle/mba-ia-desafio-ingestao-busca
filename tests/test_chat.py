import builtins

from chat import run_chat_loop


def test_run_chat_loop_recovers_from_chain_exception(monkeypatch, capsys):
    inputs = iter(["Qual o faturamento?", "sair"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    def failing_chain(pergunta: str) -> str:
        raise RuntimeError("simulated failure")

    run_chat_loop(failing_chain)

    output = capsys.readouterr().out
    assert "Erro ao processar a pergunta: simulated failure" in output
    assert "Encerrando." in output
