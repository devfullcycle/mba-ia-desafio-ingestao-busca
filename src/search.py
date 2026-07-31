import os
import re

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

# Sequências de palavras com inicial maiúscula (ex.: "Beta Mineração S.A",
# "Alfa Telecom LTDA") são tratadas como possíveis nomes de empresa citados
# na pergunta do usuário.
ENTIDADE = re.compile(r"(?:[A-ZÀ-Ý][\wÀ-ÿ]*\.?\s*)+")
SUFIXOS_VALIDOS = {"S.A", "S.A.", "LTDA", "EPP", "ME"}


def extrair_entidades(pergunta):
    entidades = []
    for match in ENTIDADE.finditer(pergunta):
        nome = match.group().strip()
        palavras = nome.split()
        if len(palavras) >= 2 or nome.upper().rstrip(".") in {
            s.rstrip(".") for s in SUFIXOS_VALIDOS
        }:
            entidades.append(nome)
    return entidades


def entidade_para_padrao_ilike(nome):
    partes = []
    wildcard_anterior = False
    for char in nome:
        if char.isalnum() and ord(char) < 128:
            partes.append(char)
            wildcard_anterior = False
        elif char.isspace():
            partes.append(" ")
            wildcard_anterior = False
        elif not wildcard_anterior:
            # Caracteres acentuados/pontuação viram um "%": o PDF tem
            # problemas de codificação que corrompem letras acentuadas,
            # então não dá para confiar no caractere exato.
            partes.append("%")
            wildcard_anterior = True
    padrao = re.sub(r"\s+", " ", "".join(partes)).strip()
    return f"%{padrao}%"

DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL")

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


def search_prompt(question=None):
    embeddings = GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)

    store = PGVector(
        embeddings=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )

    llm = ChatGoogleGenerativeAI(model=GOOGLE_LLM_MODEL, temperature=0)
    prompt = PromptTemplate(
        input_variables=["contexto", "pergunta"],
        template=PROMPT_TEMPLATE,
    )
    chain = prompt | llm | StrOutputParser()

    def ask(pergunta):
        entidades = extrair_entidades(pergunta)
        results = []

        if entidades:
            padroes = [entidade_para_padrao_ilike(nome) for nome in entidades]
            filtro = {
                "$or": [{"empresas": {"$ilike": padrao}} for padrao in padroes]
            }
            results = store.similarity_search_with_score(pergunta, k=10, filter=filtro)

        if not results:
            results = store.similarity_search_with_score(pergunta, k=10)

        contexto = "\n\n".join(doc.page_content for doc, _score in results)
        return chain.invoke({"contexto": contexto, "pergunta": pergunta})

    if question is not None:
        return ask(question)

    return ask


if __name__ == "__main__":
    pergunta = input("Faça sua pergunta: ")
    print(search_prompt(pergunta))
