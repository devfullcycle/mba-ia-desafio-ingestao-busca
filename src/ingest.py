import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    DATABASE_URL,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    create_embeddings,
    create_vector_store,
)

PDF_PATH = os.getenv("PDF_PATH")


def ingest_pdf():

    print("=" * 60)
    print("INICIANDO PROCESSO DE INGESTÃO")
    print("=" * 60)

    if not PDF_PATH:
        raise ValueError("PDF_PATH não configurado.")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não configurado.")

    if not COLLECTION_NAME:
        raise ValueError("PG_VECTOR_COLLECTION_NAME não configurado.")

    print("\n[1/5] Carregando PDF...")

    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    print(f"✓ Total de páginas: {len(documents)}")

    print("\n[2/5] Gerando chunks...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    print(f"✓ Total de chunks gerados: {len(chunks)}")

    print("\n[3/5] Inicializando modelo de embeddings...")

    embeddings = create_embeddings()

    print(f"✓ Modelo: {EMBEDDING_MODEL}")

    print("\n[4/5] Conectando ao PostgreSQL + pgVector...")

    vector_store = create_vector_store(embeddings)

    print("✓ Conexão estabelecida")

    print("\n[5/5] Persistindo chunks vetorizados...")

    vector_store.add_documents(chunks)

    print("\n✓ INGESTÃO FINALIZADA COM SUCESSO")
    print(f"✓ Collection: {COLLECTION_NAME}")
    print(f"✓ Chunks armazenados: {len(chunks)}")


if __name__ == "__main__":
    ingest_pdf()