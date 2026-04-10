from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from utils import create_vector_store

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

def get_context(query:str) -> str:
  vector_store = create_vector_store()
  docs = [k[0].page_content for k in vector_store.similarity_search_with_score(query=query,k=10)]
  return "\n---\n".join(docs)

def search_prompt(question=None):
  if question in (None, ""):
    raise ValueError("O argumento de entrada 'question' deve ser uma str não vazia.")

  prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
  add_context = RunnableLambda(lambda x: {"contexto": get_context(x["pergunta"]), "pergunta": x["pergunta"]})

  return add_context | prompt