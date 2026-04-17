import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")
PROVIDER = os.getenv("PROVIDER", "OPENAI").upper()


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


def _get_vector_store(embeddings):
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL nao configurada no .env")

    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )

def ingest_pdf():
    if not PDF_PATH:
        raise ValueError("PDF_PATH nao configurado no .env")
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF nao encontrado em: {PDF_PATH}")

    print(f"Carregando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    if not docs:
        raise ValueError("Nenhum conteudo foi extraido do PDF")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(docs)

    if not chunks:
        raise ValueError("Nenhum chunk foi gerado a partir do PDF")

    embeddings = _get_embeddings_model()
    vector_store = _get_vector_store(embeddings)

    print(f"Persistindo {len(chunks)} chunks em PGVector...")
    vector_store.add_documents(chunks)
    print("Ingestao finalizada com sucesso.")


if __name__ == "__main__":
    try:
        ingest_pdf()
    except Exception as exc:
        print(f"Erro na ingestao: {exc}")