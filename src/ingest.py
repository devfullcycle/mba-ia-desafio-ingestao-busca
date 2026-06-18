import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector

load_dotenv()

def ingest_pdf() -> None:
    
    for k in ("PGVECTOR_URL", "GEMINI_MODEL", "PGVECTOR_COLLECTION"):
        if k not in os.environ:
            raise ValueError(f"{k} is not set in the environment variables")

    pdf_path = os.getenv("PDF_PATH", "document.pdf")

    docs = PyPDFLoader(str(pdf_path)).load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                            chunk_overlap=150,
                                            add_start_index=False).split_documents(docs)

    if not splitter:
        raise ValueError("No documents were split. Please check the PDF file and the splitting parameters.")

    enriched = [
        Document(
            page_content=doc.page_content,
            metadata={k: v for k, v in doc.metadata.items() if v not in("", None)},
        )
        for doc in splitter
    ]

    ids = [f"doc-{i}" for i in range(len(enriched))]

    embedding_model = GoogleGenerativeAIEmbeddings(model=os.environ["GEMINI_MODEL"], google_api_key=os.environ["GOOGLE_API_KEY"])

    storage = PGVector(embeddings=embedding_model,
                    collection_name=os.environ["PGVECTOR_COLLECTION"],
                    connection=os.environ["PGVECTOR_URL"],
                    use_jsonb=True)

    storage.add_documents(enriched, ids=ids, embedding=embedding_model)

    print("Ingestão realizada com sucesso!")

if __name__ == "__main__":
    ingest_pdf()