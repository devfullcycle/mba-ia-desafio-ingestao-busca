from search import build_prompt


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
