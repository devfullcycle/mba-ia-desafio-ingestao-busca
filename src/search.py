import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

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

def _get_embeddings():
    load_dotenv()
    provider = (os.getenv("EMBEDDING_PROVIDER") or "").lower()
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    # 1) forçar local quando EMBEDDING_PROVIDER=local
    if provider == "local":
        model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        return HuggingFaceEmbeddings(model_name=model_name)

    # 2) gemini explícito
    if provider == "gemini":
        if not google_key:
            raise RuntimeError("GOOGLE_API_KEY ausente para provider gemini")
        model = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
        return GoogleGenerativeAIEmbeddings(model=model, google_api_key=google_key)

    # 3) default: tenta OpenAI, depois Gemini
    if openai_key:
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        return OpenAIEmbeddings(model=model, api_key=openai_key)
    if google_key:
        model = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
        return GoogleGenerativeAIEmbeddings(model=model, google_api_key=google_key)

    # 4) fallback final: local
    model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name=model_name)

def _get_vectorstore():
  """Conecta no Postgres e retorna o PGVector apontando para a coleção."""
  load_dotenv()
  database_url = os.getenv("DATABASE_URL")
  collection = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")
  if not database_url:
    raise RuntimeError("DATABASE_URL ausente")
  engine = create_engine(database_url)
  embeddings = _get_embeddings()
  return PGVector(
        connection=engine,
        collection_name=collection,
        embeddings=embeddings,
        use_jsonb=True,
    )

def similarity_search_with_score(query: str, k: int = 10):
    """Retorna lista de pares (Document, score)."""
    vs = _get_vectorstore()
    return vs.similarity_search_with_score(query, k=k)

def _build_context(docs_with_scores):
    """Concatena os textos dos documentos recuperados para virar o CONTEXTO."""
    partes = []
    for doc, score in docs_with_scores:
        texto = doc.page_content.strip()
        if texto:
            partes.append(texto)
    return "\n\n---\n\n".join(partes)

def search_prompt(question: str, k: int = 10, debug: bool = False) -> str:
    """Busca top-k, monta e retorna o prompt final preenchido."""
    resultados = similarity_search_with_score(question, k=k)

    if debug:
        print("\n[debug] top-k resultados:")
        for i, (doc, score) in enumerate(resultados, 1):
            print(f"#{i} score={score:.4f} preview={doc.page_content[:120]!r}")

    contexto = _build_context(resultados)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=question)
    return prompt