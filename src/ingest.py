import os
from dotenv import load_dotenv

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
DATABASE_URL = os.getenv("DATABASE_URL")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def ingest_pdf():
    """Lê o PDF localizado em PDF_PATH, gera chunks e salva embeddings em Postgres+pgvector.

    Requisitos:
    - chunk_size=1000, chunk_overlap=150
    - usa PyPDFLoader, RecursiveCharacterTextSplitter, OpenAIEmbeddings e PGVector
    """
    if not DATABASE_URL:
        print("DATABASE_URL não configurado. Defina a variável de ambiente.")
        return

    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings
        from langchain_postgres import PGVector
    except Exception as e:
        print("Erro ao importar dependências do LangChain:", e)
        return

    if not os.path.exists(PDF_PATH):
        print(f"PDF não encontrado em: {PDF_PATH}")
        return

    print(f"Carregando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    print(f"Gerados {len(chunks)} chunks.")

    print("Inicializando embeddings...")
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    print("Persistindo vetores no Postgres (pgvector)...")
    try:
        # Tenta criar/atualizar a tabela com os documentos
        store = PGVector.from_documents(
            documents=chunks,
            embeddings=embeddings,
            table_name="documents",
            connection_string=DATABASE_URL,
        )
        print("Ingestão concluída com sucesso.")
        print(f"Tabela utilizada: documents")
        print(f"Vetores inseridos: {len(chunks)}")
    except Exception as e:
        print("Falha ao persistir vetores:", e)


if __name__ == "__main__":
    ingest_pdf()