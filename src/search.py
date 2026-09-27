from typing import Callable, Optional

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

from config import get_settings

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

NO_DOCUMENTS_MESSAGE = (
    "Nenhum documento indexado. Rode 'python src/ingest.py' antes de fazer perguntas."
)


def build_prompt(pergunta: str, contexto: str) -> str:
    return PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)


def answer(pergunta: str, resultados, invoke: Callable[[str], str]) -> str:
    if not resultados:
        return NO_DOCUMENTS_MESSAGE

    contexto = "\n\n".join(doc.page_content for doc, _score in resultados)
    prompt = build_prompt(pergunta=pergunta, contexto=contexto)
    return invoke(prompt)


def search_prompt() -> Optional[Callable[[str], str]]:
    try:
        settings = get_settings()

        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.google_embedding_model,
            google_api_key=settings.google_api_key,
        )

        store = PGVector(
            embeddings=embeddings,
            collection_name=settings.pg_vector_collection_name,
            connection=settings.database_url,
            use_jsonb=True,
        )

        llm = ChatGoogleGenerativeAI(
            model=settings.google_llm_model,
            google_api_key=settings.google_api_key,
        )
    except Exception as exc:
        print(f"Erro ao inicializar o chat: {exc}")
        return None

    def ask(pergunta: str) -> str:
        resultados = store.similarity_search_with_score(pergunta, k=10)
        return answer(pergunta, resultados, lambda prompt: llm.invoke(prompt).content)

    return ask
