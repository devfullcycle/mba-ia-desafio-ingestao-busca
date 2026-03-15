import os
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Carrega variáveis de ambiente
load_dotenv()

# Configurações via .env
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_embeddings():
    """Retorna o modelo de embeddings Google."""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY não configurada no arquivo .env")
    if not EMBEDDING_MODEL:
        raise ValueError("GOOGLE_EMBEDDING_MODEL não configurada no arquivo .env")
    
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )

def search_documents(query: str) -> str:
    """
    Busca documentos relevantes no banco vetorial e retorna os textos concatenados.
    
    Args:
        query: Texto da consulta para buscar documentos similares
        
    Returns:
        String com os textos dos documentos encontrados concatenados,
        prontos para serem usados como contexto para uma LLM
        
    Raises:
        ValueError: Se a GOOGLE_API_KEY não estiver configurada
        Exception: Se houver erros na conexão com o banco
    """
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não configurada no .env")
    if not COLLECTION_NAME:
        raise ValueError("PG_VECTOR_COLLECTION_NAME não configurada no .env")

    # Obtém o modelo de embeddings
    embeddings = get_embeddings()
    
    # Conecta ao vectorstore PostgreSQL
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )
    
    # Busca vetorial usando similarity_search_with_score
    # Retorna os 10 documentos mais relevantes com suas pontuações
    results = vectorstore.similarity_search_with_score(
        query=query,
        k=10
    )
    
    # Extrai os textos dos documentos e concatena
    # results é uma lista de tuplas (Document, score)
    texts = [doc.page_content for doc, _ in results]
    
    # Concatena os textos com separador duplo de linha
    context = "\n\n".join(texts)
    
    return context


if __name__ == "__main__":
    # Exemplo de uso da função search_documents
    import sys
    
    if len(sys.argv) > 1:
        # Se passar argumentos, usa como query
        query = " ".join(sys.argv[1:])
    else:
        # Query padrão para teste
        query = "Qual o conteúdo principal do documento?"
    
    print("=" * 60)
    print("🔍 BUSCA VETORIAL DE DOCUMENTOS")
    print("=" * 60)
    print(f"\n📝 Query: {query}\n")
    
    try:
        context = search_documents(query)
        print("✅ Documentos encontrados!")
        print("\n" + "=" * 60)
        print("📄 CONTEXTO RETORNADO:")
        print("=" * 60)
        print(context)
        print("\n" + "=" * 60)
        print(f"📊 Total de caracteres: {len(context)}")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\nVerifique se:")
        print("  1. O PostgreSQL está rodando")
        print("  2. A ingestão foi executada")
        print("  3. GOOGLE_API_KEY e GOOGLE_EMBEDDING_MODEL estão configuradas")