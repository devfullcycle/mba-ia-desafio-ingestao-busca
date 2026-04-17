import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")
PROVIDER = os.getenv("PROVIDER", "OPENAI").upper()
SEARCH_PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompts" / "search_prompt_template.md"


def _load_search_prompt_template() -> str:
  if not SEARCH_PROMPT_TEMPLATE_PATH.exists():
    raise FileNotFoundError(
      f"Arquivo de prompt nao encontrado: {SEARCH_PROMPT_TEMPLATE_PATH}"
    )

  return SEARCH_PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")


def _get_embeddings_model():
  if PROVIDER == "OPENAI":
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
      raise ValueError("OPENAI_API_KEY nao configurada no .env")
    return OpenAIEmbeddings(model=model, api_key=api_key)

  if PROVIDER == "GOOGLE":
    model = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
      raise ValueError("GOOGLE_API_KEY nao configurada no .env")
    return GoogleGenerativeAIEmbeddings(model=model, google_api_key=api_key)

  raise ValueError("PROVIDER invalido. Use OPENAI ou GOOGLE")


def _get_vector_store():
  if not DATABASE_URL:
    raise ValueError("DATABASE_URL nao configurada no .env")

  embeddings = _get_embeddings_model()
  return PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=DATABASE_URL,
    use_jsonb=True,
  )


def search_context(query: str, k: int = 10) -> str:
  if not query or not query.strip():
    return ""

  vector_store = _get_vector_store()
  results = vector_store.similarity_search_with_score(query, k=k)

  if not results:
    return ""

  parts = []
  for doc, score in results:
    score_text = f"{score:.6f}" if isinstance(score, float) else str(score)
    chunk_text = (doc.page_content or "").strip()
    if not chunk_text:
      continue
    parts.append(f"[score={score_text}]\n{chunk_text}")

  return "\n\n---\n\n".join(parts)


PROMPT_TEMPLATE = _load_search_prompt_template()

def search_prompt(question: str) -> str:
  contexto = search_context(question, k=10)
  if not contexto:
    contexto = ""

  return PROMPT_TEMPLATE.format(contexto=contexto, pergunta=question)