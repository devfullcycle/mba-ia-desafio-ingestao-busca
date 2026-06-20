import os

from config import DATABASE_URL, COLLECTION_NAME, EMBEDDING_MODEL

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGVector
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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


def _get_vector_store() -> PGVector:
    """Instancia e retorna o PGVector conectado ao banco."""
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )
    return vector_store


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

    # Inicializa o vector store UMA VEZ
    try:
        vector_store = _get_vector_store()
    except Exception as e:
        print(f"ERRO ao inicializar embeddings ou conexão com banco: {e}")
        return None

    def buscar_contexto(query: str, k: int = 10) -> str:
        """
        Busca os k documentos mais similares à query no banco vetorial.
        Retorna os textos concatenados como uma string única.
        """
        resultados = vector_store.similarity_search_with_score(query, k=k)
        textos = [doc.page_content for doc, _score in resultados]
        return "\n\n".join(textos)

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-3.1-flash-lite-preview",
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