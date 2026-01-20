import os
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

PROMPT_TEMPLATE = """
CONTEXTO:
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

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def get_embeddings():
    """
    Retorna o modelo de embeddings configurado.
    Prioriza Google Gemini, mas usa OpenAI se Google não estiver disponível.
    """
    if GOOGLE_API_KEY:
        return GoogleGenerativeAIEmbeddings(
            model=GOOGLE_EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY
        )
    elif OPENAI_API_KEY:
        return OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
    else:
        raise ValueError("É necessário configurar GOOGLE_API_KEY ou OPENAI_API_KEY no arquivo .env")


def get_llm():
    """
    Retorna o modelo de LLM configurado.
    Prioriza Google Gemini, mas usa OpenAI se Google não estiver disponível.
    """
    if GOOGLE_API_KEY:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0
        )
    elif OPENAI_API_KEY:
        return ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=OPENAI_API_KEY,
            temperature=0
        )
    else:
        raise ValueError("É necessário configurar GOOGLE_API_KEY ou OPENAI_API_KEY no arquivo .env")


def search_prompt(question=None):
    """
    Cria e retorna uma chain de RAG (Retrieval Augmented Generation).

    Se uma pergunta for fornecida, executa a busca e retorna a resposta.
    Caso contrário, apenas retorna a chain configurada.
    """
    # Validar configurações
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não está configurado no arquivo .env")

    if not PG_VECTOR_COLLECTION_NAME:
        raise ValueError("PG_VECTOR_COLLECTION_NAME não está configurado no arquivo .env")

    # Configurar embeddings
    embeddings = get_embeddings()

    # Conectar ao vector store
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )

    # Configurar o retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    # Configurar o LLM
    llm = get_llm()

    # Criar o prompt
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    # Criar a chain de RAG
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    # Se uma pergunta foi fornecida, executar a busca
    if question:
        result = chain.invoke({"query": question})
        return result

    # Caso contrário, retornar a chain configurada
    return chain