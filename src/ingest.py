import os
import sys

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").strip().lower()


def get_embeddings():
    print(f"----- Configurando embeddings ({EMBEDDING_PROVIDER}) -----")
    if EMBEDDING_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings

        model = os.getenv("OPENAI_EMBEDDING_MODEL")
        if not os.getenv("OPENAI_API_KEY") or not model:
            raise ValueError(
                "OPENAI_API_KEY e OPENAI_EMBEDDING_MODEL são obrigatórios "
                "quando EMBEDDING_PROVIDER=openai"
            )
        print(f"---- Usando OpenAIEmbeddings ({model}) ----")
        return OpenAIEmbeddings(model=model)

    if EMBEDDING_PROVIDER == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        model = os.getenv("GOOGLE_EMBEDDING_MODEL")
        if not os.getenv("GOOGLE_API_KEY") or not model:
            raise ValueError(
                "GOOGLE_API_KEY e GOOGLE_EMBEDDING_MODEL são obrigatórios "
                "quando EMBEDDING_PROVIDER=google"
            )
        print(f"---- Usando GoogleGenerativeAIEmbeddings ({model}) ----")
        return GoogleGenerativeAIEmbeddings(model=model)

    raise ValueError(
        f"EMBEDDING_PROVIDER inválido: '{EMBEDDING_PROVIDER}'. "
        "Use 'openai' ou 'google'."
    )


def ingest_pdf():
    print("---- Gustavo Chagas Bezerra ----")
    print("----- Iniciando ingestão do PDF -----")

    required = {
        "PDF_PATH": PDF_PATH,
        "DATABASE_URL": DATABASE_URL,
        "PG_VECTOR_COLLECTION_NAME": PG_VECTOR_COLLECTION_NAME,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(f"Variáveis de ambiente ausentes: {', '.join(missing)}")

    if not os.path.isfile(PDF_PATH):
        raise FileNotFoundError(f"PDF não encontrado: {PDF_PATH}")

    print(f"---- Carregando PDF ({PDF_PATH}) ----")
    documents = PyPDFLoader(PDF_PATH).load()
    print(f"----- PDF carregado: {len(documents)} páginas -----")

    print("---- Dividindo em chunks (1000 / overlap 150) ----")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    print(f"----- {len(chunks)} chunks gerados -----")

    print("---- Gerando embeddings e salvando no PGVector ----")
    embeddings = get_embeddings()
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        pre_delete_collection=True,
    )

    print(
        f"----- Ingestão concluída: {len(chunks)} chunks "
        f"(provider={EMBEDDING_PROVIDER}, collection={PG_VECTOR_COLLECTION_NAME}) -----"
    )


if __name__ == "__main__":
    try:
        ingest_pdf()
    except Exception as exc:
        print(f"---- Erro na ingestão: {exc} ----", file=sys.stderr)
        sys.exit(1)
