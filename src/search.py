from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

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

  GPT_NANO = "gpt-5-nano"
  print(question)

  messages_template = [
    ("system",PROMPT_TEMPLATE)
  ]

  prompt = ChatPromptTemplate.from_messages(messages_template)

  llm = ChatOpenAI(model=GPT_NANO,temperature=0.9, disable_streaming=True)

  chain = prompt | llm  
  result = chain.invoke({"contexto":get_context(query=question),"pergunta":question})

  print(result.content)

  # Alfa Agronegócio Indústria