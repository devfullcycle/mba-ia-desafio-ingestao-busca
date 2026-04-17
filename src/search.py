import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGEngine, PGVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- Configuração ---
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "document_embeddings")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")

# --- Prompt Template (conforme spec.md) ---
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


def _get_vector_store() -> PGVectorStore:
    """Instancia e retorna o PGVectorStore conectado ao banco."""
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    engine = PGEngine.from_connection_string(url=DATABASE_URL)
    vector_store = PGVectorStore.create_sync(
        engine=engine,
        table_name=COLLECTION_NAME,
        embedding_service=embeddings,
    )
    return vector_store


def buscar_contexto(query: str, k: int = 10) -> str:
    """
    Busca os k documentos mais similares à query no banco vetorial.
    Retorna os textos concatenados como uma string única.
    """
    vector_store = _get_vector_store()
    resultados = vector_store.similarity_search_with_score(query, k=k)

    # Cada resultado é uma tupla (Document, score)
    textos = [doc.page_content for doc, _score in resultados]
    return "\n\n".join(textos)


def search_prompt():
    """
    Retorna um dicionário com os componentes necessários para o chat:
    - 'chain': LCEL chain (prompt | llm | StrOutputParser)
    - 'buscar_contexto': função de busca vetorial

    Retorna None se houver erro de configuração.
    """
    if not DATABASE_URL:
        print("ERRO: DATABASE_URL não configurada no .env")
        return None
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERRO: GOOGLE_API_KEY não configurada no .env")
        return None

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
    )

    prompt = PromptTemplate(
        input_variables=["contexto", "pergunta"],
        template=PROMPT_TEMPLATE,
    )

    chain = prompt | llm | StrOutputParser()

    return {
        "chain": chain,
        "buscar_contexto": buscar_contexto,
    }