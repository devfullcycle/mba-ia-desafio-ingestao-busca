import os
from dotenv import load_dotenv

from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()


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
{user_question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):

    embedding_model = GoogleGenerativeAIEmbeddings(model=os.environ["GEMINI_MODEL"], google_api_key=os.environ["GOOGLE_API_KEY"])

    storage = PGVector(embeddings=embedding_model,
                    collection_name=os.environ["PGVECTOR_COLLECTION"],
                    connection=os.environ["PGVECTOR_URL"])

    results = storage.similarity_search_with_score(question, k=10)

    return PROMPT_TEMPLATE.format(contexto=results, user_question=question)
