import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

def main():
    load_dotenv()

    pdf_path = os.getenv("PDF_PATH")
    openai_key = os.getenv("GOOGLE_API_KEY")
    pg_url = os.getenv("PGVECTOR_URL")
    collection = os.getenv("PGVECTOR_COLLECTION", "default_collection")
    
    embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")    

    if not openai_key:
        raise RuntimeError("GOOGLE_API_KEY não encontrada no .env")
    if not pg_url:
        raise RuntimeError("PGVECTOR_URL não encontrada no .env")

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
    )
    chunks = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)

    vectorstore = PGVector(
        connection=pg_url,
        embeddings=embeddings,
        collection_name=collection,
        use_jsonb=True,
    )

    vectorstore.add_documents(chunks)
    print(f"Ingestão concluída: {len(chunks)} chunks na collection '{collection}'.")

if __name__ == "__main__":
    main()
