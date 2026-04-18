import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")

def ingest_pdf():
    """
    Função principal para ingestão do PDF:
    1. Carrega o PDF
    2. Divide em chunks de 1000 caracteres com overlap de 150
    3. Converte cada chunk em embedding
    4. Armazena os vetores no PostgreSQL com pgVector
    """
    for k in ("DATABASE_URL","GOOGLE_API_KEY"):
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")

    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    # O PDF deve ser dividido em chunks de 1000 caracteres com overlap de 150.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150, 
        add_start_index=False
    )
    splits = text_splitter.split_documents(docs)
    
    if not splits:
        raise SystemExit(0)
    
    # Cada chunk deve ser convertido em embedding.
    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDING_MODEL")
    )

    # Os vetores devem ser armazenados no banco de dados PostgreSQL com pgVector.
    connection_string = os.getenv("DATABASE_URL")
    
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=connection_string,
        use_jsonb=True,
    )

    # Adicionar os documentos ao vector store (isso converte em embeddings e armazena)
    store.add_documents(splits)
    print(f"{len(splits)} chunks foram processados e armazenados no banco de dados")
    
    return store


if __name__ == "__main__":
    ingest_pdf()