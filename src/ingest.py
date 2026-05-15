from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DATABASE_URL,
    _resolve_pdf_path,
    get_embeddings,
)


def ingest() -> None:
    pdf = _resolve_pdf_path()

    # 1. Lê o PDF
    print("Carregando PDF...")
    documents = PyPDFLoader(str(pdf)).load()
    print(f"{len(documents)} páginas carregadas.")

    # 2. Divide em chunks
    print("Dividindo em chunks...")
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    ).split_documents(documents)
    print(f"{len(chunks)} chunks gerados.")

    # 3. Embeddings + PGVector
    print("Gerando embeddings e salvando no banco...")
    PGVector.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        pre_delete_collection=True,
    )

    print("Ingestão concluída com sucesso!")


if __name__ == "__main__":
    ingest()
