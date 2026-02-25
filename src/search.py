import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.documents import Document

load_dotenv()

for k in ("DATABASE_URL", "PG_VECTOR_COLLECTION_NAME"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

SYSTEM_PROMPT_TEMPLATE = """CONTEXTO:
{context}

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

HISTÓRICO DA CONVERSA:
{history}

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO\""""

_prompt = PromptTemplate(
    input_variables=["context", "history", "question"],
    template=SYSTEM_PROMPT_TEMPLATE,
)

_CONFIG_BY_DIM = {
    1536: {
        "label": "OpenAI  — embedding: text-embedding-3-small | chat: gpt-5-nano",
        "embedding": lambda: OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")),
        "llm":       lambda: ChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL", "gpt-5-nano")),
    },
    3072: {
        "label": "Gemini  — embedding: gemini-embedding-001 | chat: gemini-2.5-flash",
        "embedding": lambda: GoogleGenerativeAIEmbeddings(model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001")),
        "llm":       lambda: ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_CHAT_MODEL", "gemini-2.5-flash")),
    },
}

_embeddings = None
_llm = None


def search_documents(query: str) -> str:
    """Search the internal document store and return relevant passages for the given query."""
    store = PGVector(
        embeddings=_embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )
    results = store.similarity_search_with_score(query, k=10)
    return "\n\n".join(doc.page_content for doc, _score in results)


def build_db_context_summary(llm) -> str:
    """Fetch all documents from the DB and summarize them via Map-Reduce.

    Utility function — useful for generating an overview of the indexed content.
    Not called during startup to avoid unnecessary LLM calls.
    """
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT e.document
            FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON e.collection_id = c.uuid
            WHERE c.name = :name
            ORDER BY e.id
        """), {"name": os.getenv("PG_VECTOR_COLLECTION_NAME")}).fetchall()

    if not rows:
        return ""

    docs = [Document(page_content=row[0]) for row in rows]

    map_prompt = PromptTemplate.from_template(
        "Escreva um resumo conciso do seguinte trecho:\n{context}"
    )
    map_chain = map_prompt | llm | StrOutputParser()

    reduce_prompt = PromptTemplate.from_template(
        "Combine os seguintes resumos em um único resumo conciso:\n{context}"
    )
    reduce_chain = reduce_prompt | llm | StrOutputParser()

    prepare_map_inputs = RunnableLambda(lambda d: [{"context": doc.page_content} for doc in d])
    prepare_reduce_input = RunnableLambda(lambda summaries: {"context": "\n".join(summaries)})

    pipeline = prepare_map_inputs | map_chain.map() | prepare_reduce_input | reduce_chain

    return pipeline.invoke(docs)


def init_agent(llm, embeddings) -> None:
    global _llm, _embeddings
    _llm = llm
    _embeddings = embeddings


def init_agent_from_db() -> str:
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT vector_dims(e.embedding)
            FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON e.collection_id = c.uuid
            WHERE c.name = :name
            LIMIT 1
        """), {"name": os.getenv("PG_VECTOR_COLLECTION_NAME")}).fetchone()

    if row is None:
        raise RuntimeError("Nenhum embedding encontrado. Execute o ingest primeiro.")

    dim = row[0]
    config = _CONFIG_BY_DIM.get(dim)
    if config is None:
        raise RuntimeError(f"Dimensão desconhecida: {dim}. Suportadas: {list(_CONFIG_BY_DIM)}")

    init_agent(config["llm"](), config["embedding"]())
    return config["label"]


_session_store: dict[str, InMemoryChatMessageHistory] = {}


def _get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _session_store:
        _session_store[session_id] = InMemoryChatMessageHistory()
    return _session_store[session_id]


def search_prompt(question: str, session_id: str = "default") -> str:
    history = _get_session_history(session_id)

    history_text = "\n".join(
        f"{'Usuário' if msg.type == 'human' else 'Assistente'}: {msg.content}"
        for msg in history.messages
    )

    context = search_documents(question)
    full_prompt = _prompt.format(context=context, history=history_text, question=question)

    raw = _llm.invoke(full_prompt).content
    if isinstance(raw, list):
        answer = next((b["text"] for b in raw if isinstance(b, dict) and b.get("type") == "text"), str(raw))
    else:
        answer = raw

    history.add_user_message(question)
    history.add_ai_message(answer)

    return answer
