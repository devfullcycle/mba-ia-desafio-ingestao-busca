from langchain_core.documents import Document

from search import NO_DOCUMENTS_MESSAGE, answer, build_prompt


def test_build_prompt_includes_context_and_question():
    prompt = build_prompt(
        pergunta="Qual o faturamento da Empresa SuperTechIABrazil?",
        contexto="SuperTechIABrazil R$ 10.000.000,00 2025",
    )

    assert "SuperTechIABrazil R$ 10.000.000,00 2025" in prompt
    assert "Qual o faturamento da Empresa SuperTechIABrazil?" in prompt
    assert "Não tenho informações necessárias para responder sua pergunta." in prompt


def test_build_prompt_keeps_rules_intact():
    prompt = build_prompt(pergunta="qualquer pergunta", contexto="qualquer contexto")

    assert "Nunca invente ou use conhecimento externo." in prompt
    assert 'RESPONDA A "PERGUNTA DO USUÁRIO"' in prompt


def test_answer_returns_message_when_no_results():
    resposta = answer(
        pergunta="Qualquer pergunta",
        resultados=[],
        invoke=lambda prompt: "não deveria ser chamado",
    )

    assert resposta == NO_DOCUMENTS_MESSAGE


def test_answer_invokes_llm_with_built_prompt_when_results_exist():
    doc = Document(page_content="SuperTechIABrazil R$ 10.000.000,00 2025")
    captured_prompts = []

    def fake_invoke(prompt: str) -> str:
        captured_prompts.append(prompt)
        return "R$ 10.000.000,00"

    resposta = answer(
        pergunta="Qual o faturamento da Empresa SuperTechIABrazil?",
        resultados=[(doc, 0.1)],
        invoke=fake_invoke,
    )

    assert resposta == "R$ 10.000.000,00"
    assert len(captured_prompts) == 1
    assert "SuperTechIABrazil R$ 10.000.000,00 2025" in captured_prompts[0]
    assert "Qual o faturamento da Empresa SuperTechIABrazil?" in captured_prompts[0]
