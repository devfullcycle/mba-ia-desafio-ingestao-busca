import os
import re
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Carrega variáveis de ambiente
load_dotenv()

# Configurações via .env
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
PDF_PATH = os.getenv("PDF_PATH")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")

def ingest_pdf():
    """
    Realiza a ingestão de um PDF no PostgreSQL com pgvector.
    
    Fluxo:
    1. Carrega o PDF usando PyPDFLoader
    2. Divide em chunks de 1000 caracteres com overlap de 150
    3. Gera embeddings usando Google (models/gemini-embedding-001)
    4. Armazena no PostgreSQL usando PGVector
    """
    
    print("=" * 60)
    print("🚀 INICIANDO INGESTÃO DO PDF")
    print("=" * 60)
    
    # Validações
    if not PDF_PATH or not os.path.exists(PDF_PATH):
        print(f"\n❌ Erro: Arquivo '{PDF_PATH}' não encontrado!")
        print("Configure PDF_PATH no .env e garanta que o arquivo exista.")
        return
    
    if not DATABASE_URL:
        print("\n❌ Erro: DATABASE_URL não configurada no .env")
        return

    if not COLLECTION_NAME:
        print("\n❌ Erro: PG_VECTOR_COLLECTION_NAME não configurada no .env")
        return

    if not GOOGLE_API_KEY:
        print("\n❌ Erro: GOOGLE_API_KEY não configurada no .env")
        return

    if not EMBEDDING_MODEL:
        print("\n❌ Erro: GOOGLE_EMBEDDING_MODEL não configurada no .env")
        return
    
    # Passo 1: Carregar o PDF
    print(f"\n📄 [1/4] Carregando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"    ✓ {len(documents)} página(s) carregada(s) com sucesso")
    
    # Passo 2: Dividir em chunks
    print(f"\n✂️  [2/4] Dividindo texto em chunks...")
    print(f"    - Tamanho do chunk: 1000 caracteres")
    print(f"    - Overlap: 150 caracteres")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"    ✓ {len(chunks)} chunks criados com sucesso")
    
    # Passo 3: Inicializar embeddings
    print(f"\n🧠 [3/4] Inicializando modelo de embeddings...")
    print(f"    - Modelo: {EMBEDDING_MODEL}")
    print("    - Provider: Google")
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )
    print(f"    ✓ Modelo inicializado com sucesso")
    
    # Passo 4: Armazenar no PostgreSQL
    masked_url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", DATABASE_URL or "")
    print(f"\n💾 [4/4] Armazenando vetores no PostgreSQL...")
    print(f"    - Database URL: {masked_url}")
    print(f"    - Coleção: {COLLECTION_NAME}")
    print(f"    - Gerando embeddings e salvando...")
    
    try:
        PGVector.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            connection=DATABASE_URL,
            pre_delete_collection=True,
        )
        print(f"    ✓ Vetores armazenados com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao armazenar no banco: {e}")
        print("\nVerifique se o PostgreSQL está rodando:")
        print("  docker-compose up -d")
        return
    
    # Resumo final
    print("\n" + "=" * 60)
    print("✅ INGESTÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print(f"\n📊 Resumo:")
    print(f"   • Páginas processadas: {len(documents)}")
    print(f"   • Chunks criados: {len(chunks)}")
    print(f"   • Embeddings gerados: {len(chunks)}")
    print(f"   • Banco de dados: {masked_url}")
    print(f"   • Coleção: {COLLECTION_NAME}")
    print(f"\n💡 Próximo passo: Execute 'python src/chat.py' para fazer perguntas!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    ingest_pdf()