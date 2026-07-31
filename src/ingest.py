import os
import re

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")

# Linhas do PDF seguem o padrão "Nome da empresa R$ valor ano".
# Extraímos o nome de cada linha para permitir filtrar chunks por empresa
# citada na pergunta, complementando a busca puramente vetorial.
EMPRESA_LINE = re.compile(r"^(?P<nome>.+?)\s+R\$\s*[\d.,]+\s+\d{4}\s*$", re.MULTILINE)


def extrair_empresas(texto):
    return [m.group("nome").strip() for m in EMPRESA_LINE.finditer(texto)]


def ingest_pdf():
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    for chunk in chunks:
        empresas = extrair_empresas(chunk.page_content)
        if empresas:
            chunk.metadata["empresas"] = " | ".join(empresas)

    embeddings = GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)

    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
        pre_delete_collection=True,
    )

    print(f"Ingestão concluída: {len(chunks)} chunks salvos no banco de dados.")


if __name__ == "__main__":
    ingest_pdf()
