import os

from dotenv import load_dotenv
from langchain_postgres import PGVector

from ingest import EMBEDDING_PROVIDER, get_embeddings

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")

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


def get_llm():
    print("----- Configurando LLM -----")
    if EMBEDDING_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        model = os.getenv("OPENAI_CHAT_MODEL")
        if not os.getenv("OPENAI_API_KEY") or not model:
            raise ValueError(
                "OPENAI_API_KEY e OPENAI_CHAT_MODEL são obrigatórios "
                "quando EMBEDDING_PROVIDER=openai"
            )
        print(f"---- Usando ChatOpenAI ({model}) ----")
        return ChatOpenAI(model=model)

    if EMBEDDING_PROVIDER == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = os.getenv("GOOGLE_CHAT_MODEL")
        if not os.getenv("GOOGLE_API_KEY") or not model:
            raise ValueError(
                "GOOGLE_API_KEY e GOOGLE_CHAT_MODEL são obrigatórios "
                "quando EMBEDDING_PROVIDER=google"
            )
        print(f"---- Usando ChatGoogleGenerativeAI ({model}) ----")
        return ChatGoogleGenerativeAI(model=model)

    raise ValueError(
        f"EMBEDDING_PROVIDER inválido: '{EMBEDDING_PROVIDER}'. "
        "Use 'openai' ou 'google'."
    )


def search_prompt(question=None):
    print("---- Gustavo Chagas Bezerra ----")
    print("----- Inicializando busca semântica -----")

    try:
        if not DATABASE_URL or not PG_VECTOR_COLLECTION_NAME:
            raise ValueError(
                "DATABASE_URL e PG_VECTOR_COLLECTION_NAME são obrigatórios"
            )

        print("----- Criando embeddings -----")
        embeddings = get_embeddings()

        print("---- Conectando ao PostgreSQL / pgVector ----")
        store = PGVector(
            embeddings=embeddings,
            collection_name=PG_VECTOR_COLLECTION_NAME,
            connection=DATABASE_URL,
            use_jsonb=True,
        )

        llm = get_llm()
    except Exception as exc:
        print(f"---- Erro na inicialização da busca: {exc} ----")
        return None

    def ask(q: str) -> str:
        print("---- Gustavo Chagas Bezerra ----")
        print(f"----- Vetorizando pergunta: {q} -----")
        print("---- Buscando os 10 resultados mais relevantes (k=10) ----")
        results = store.similarity_search_with_score(q, k=10)

        print(f"----- {len(results)} documentos recuperados -----")
        contexto = "\n\n".join(doc.page_content for doc, _score in results)

        print("---- Montando prompt com contexto ----")
        prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=q)

        print("----- Chamando a LLM -----")
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)
        print("---- Resposta da LLM recebida ----")
        return answer

    if question is not None:
        return ask(question)

    print("----- Busca pronta para uso -----")
    return ask
