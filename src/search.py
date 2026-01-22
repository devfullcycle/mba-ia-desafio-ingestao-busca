import os
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

load_dotenv()
for k in ("GOOGLE_EMBEDDING_MODEL", "GOOGLE_MODEL", "DATABASE_URL","PG_VECTOR_COLLECTION_NAME"):
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")

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
template_chat_input = PromptTemplate(
    input_variables=["contexto", "pergunta"],
    template=PROMPT_TEMPLATE
)

def search_prompt(question=None) -> str:
    contexto = get_context(question)
    llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL","gemini-2.5-flash-lite"))
    chain = template_chat_input | llm
    response = chain.invoke({"contexto": contexto, "pergunta": question})
    return response.content

def get_context(question=None) -> str:
    embeddings = GoogleGenerativeAIEmbeddings(model=os.getenv("GOOGLE_EMBEDDING_MODEL","models/embedding-001"))

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    results = store.similarity_search_with_score(question, k=10)

    result_str = ""
    for i, (doc, score) in enumerate(results, start=1):
        result_str += "="*50 + "\n"
        result_str += f"Resultado {i} (score: {score:.2f}):\n"
        result_str += "="*50 + "\n"
        result_str += "\nTexto:\n\n"
        result_str += "\nColunas: Nome da Empresa /  Faturamento / Ano de Fundacao \n\n"
        result_str += doc.page_content.strip() + "\n"

    return result_str
