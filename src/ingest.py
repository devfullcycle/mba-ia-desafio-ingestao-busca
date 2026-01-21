import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")


def get_embeddings():
    """
    Retorna o modelo de embeddings configurado.
    Prioriza Google Gemini, mas usa OpenAI se Google não estiver disponível.
    """
    if GOOGLE_API_KEY:
        print(f"Usando Google Embeddings: {GOOGLE_EMBEDDING_MODEL}")
        return GoogleGenerativeAIEmbeddings(
            model=GOOGLE_EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY
        )
    elif OPENAI_API_KEY:
        print(f"Usando OpenAI Embeddings: {OPENAI_EMBEDDING_MODEL}")
        return OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
    else:
        raise ValueError("É necessário configurar GOOGLE_API_KEY ou OPENAI_API_KEY no arquivo .env")


def ingest_pdf():
    """
    Faz a ingestão de um PDF no banco de dados vetorial.

    Etapas:
    1. Carrega o PDF
    2. Divide o texto em chunks
    3. Gera embeddings
    4. Armazena no PostgreSQL com pgvector
    """
    # Validar configurações
    if not PDF_PATH:
        raise ValueError("PDF_PATH não está configurado no arquivo .env")

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF não encontrado: {PDF_PATH}")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não está configurado no arquivo .env")

    if not PG_VECTOR_COLLECTION_NAME:
        raise ValueError("PG_VECTOR_COLLECTION_NAME não está configurado no arquivo .env")

    print(f"Iniciando ingestão do PDF: {PDF_PATH}")

    # 1. Carregar o PDF
    print("Carregando documento...")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"✓ Documento carregado: {len(documents)} páginas")

    # 2. Dividir em chunks
    print("Dividindo documento em chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✓ Documento dividido: {len(chunks)} chunks")

    # 3. Configurar embeddings
    print("Configurando embeddings...")
    embeddings = get_embeddings()
    print("✓ Embeddings configurados")

    # 4. Armazenar no banco de dados vetorial
    print("Armazenando no banco de dados vetorial...")
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )

    # Adicionar documentos ao vector store
    vector_store.add_documents(chunks)
    print(f"✓ {len(chunks)} chunks armazenados com sucesso no banco de dados!")

    print("\n" + "="*50)
    print("Ingestão concluída com sucesso!")
    print("="*50)


if __name__ == "__main__":
    try:
        ingest_pdf()
    except Exception as e:
        print(f"\nErro durante a ingestão: {str(e)}")
        raise
