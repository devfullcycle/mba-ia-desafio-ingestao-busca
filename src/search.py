from openai import OpenAI
from langchain_core.runnables import RunnableLambda

from config import (
    OPENAI_API_KEY,
    create_embeddings,
    create_vector_store,
)

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def _search_prompt(question=None):

    if not question:
        raise ValueError("A pergunta é obrigatória.")

    embeddings = create_embeddings()

    vector_store = create_vector_store(embeddings)

    results = vector_store.similarity_search_with_score(
        question,
        k=10
    )

    if not results:
        return "Não tenho informações necessárias para responder sua pergunta."

    context = "\n\n".join(
        doc.page_content
        for doc, score in results
    )

    prompt = PROMPT_TEMPLATE.format(
        contexto=context,
        pergunta=question
    )

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )

    return response.output_text.strip()

search_prompt = RunnableLambda(_search_prompt)