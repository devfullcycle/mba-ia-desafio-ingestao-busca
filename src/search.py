from langchain_core.documents import Document

from config import SEARCH_K, get_llm, get_vectorstore

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


def retrieve_context(question: str, k: int = SEARCH_K) -> list[tuple[Document, float]]:
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search_with_score(question, k=k)


def build_prompt(question: str, context: str) -> str:
    return PROMPT_TEMPLATE.format(contexto=context, pergunta=question)


def search_prompt(question: str) -> str:
    results = retrieve_context(question)
    context = "\n\n---\n\n".join(doc.page_content for doc, _score in results)
    prompt = build_prompt(question, context)
    response = get_llm().invoke(prompt)
    return response.content.strip()
