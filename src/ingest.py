import sys
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import ValidationError

from config import get_settings


def ingest_pdf() -> None:
    try:
        settings = get_settings()
    except ValidationError as exc:
        print(f"Erro de configuração: {exc}")
        sys.exit(1)

    pdf_path = Path(settings.pdf_path)
    if not pdf_path.exists():
        print(f"Erro: PDF não encontrado em '{pdf_path}'.")
        sys.exit(1)

    documents = PyPDFLoader(str(pdf_path)).load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.google_embedding_model,
        google_api_key=settings.google_api_key,
    )

    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=settings.pg_vector_collection_name,
        connection=settings.database_url,
        use_jsonb=True,
        pre_delete_collection=True,
    )

    print(
        f"Ingestão concluída: {len(chunks)} chunks indexados a partir de '{pdf_path.name}'."
    )


if __name__ == "__main__":
    ingest_pdf()
