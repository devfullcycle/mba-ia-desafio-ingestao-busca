import os

import truststore
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

# Usa o armazenamento de certificados do sistema (funciona em redes com
# interceptação SSL/VPN corporativa, sem desativar a verificação).
truststore.inject_into_ssl()

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
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

# String de conexão com o PostgreSQL (mesmo padrão do docker-compose.yml)
DB_CONNECTION = os.getenv(
    "DB_CONNECTION",
    "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
)

# Nome da coleção (tabela) onde os vetores foram salvos na ingestão
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "desafio_ingestao_busca")

# Modelos do Google (podem ser sobrescritos no .env)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")


def _conectar_banco():
    """Conecta ao banco vetorial usando o MESMO modelo de embeddings da ingestão."""
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        transport="rest",
    )
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
    )


def search_prompt(question):
    """
    Recebe uma pergunta e retorna a resposta gerada pela LLM.

    Passos:
    1. Vetoriza a pergunta e busca os 10 trechos mais relevantes (k=10).
    2. Junta os trechos encontrados no CONTEXTO do prompt.
    3. Chama a LLM (Gemini) e retorna a resposta.
    """
    vector_store = _conectar_banco()

    # 1. Busca os 10 resultados mais relevantes no banco vetorial
    resultados = vector_store.similarity_search_with_score(question, k=10)
    # Menor distância = mais relevante (ordenação crescente)
    resultados = sorted(resultados, key=lambda item: item[1])

    if not resultados:
        contexto = "Não há dados no banco."
    else:
        contexto = "\n\n".join(doc.page_content for doc, _ in resultados)

    # 2. Monta o prompt com o contexto e chama a LLM
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0, transport="rest")
    chain = prompt | llm

    resposta = chain.invoke({"contexto": contexto, "pergunta": question})
    return resposta.content
