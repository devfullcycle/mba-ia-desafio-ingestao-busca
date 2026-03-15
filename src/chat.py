import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from search import search_documents

# Carrega variáveis de ambiente
load_dotenv()

LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite")

# Template do prompt exatamente como especificado
PROMPT_TEMPLATE = """CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
"Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A PERGUNTA DO USUÁRIO"""

def _build_llm() -> ChatGoogleGenerativeAI:
    """Instancia o LLM uma única vez, validando a API key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não configurada no arquivo .env")
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=api_key,
        temperature=0,
    )

def ask_llm(llm: ChatGoogleGenerativeAI, context: str, question: str) -> str:
    """
    Envia o contexto e a pergunta para a LLM e retorna a resposta.
    
    Args:
        llm: Instância reutilizável do modelo LLM
        context: Contexto recuperado da busca vetorial
        question: Pergunta do usuário
        
    Returns:
        Resposta gerada pela LLM
    """
    prompt = PROMPT_TEMPLATE.format(
        contexto=context,
        pergunta=question
    )
    response = llm.invoke(prompt)
    return response.content

def main():
    """Loop principal do chat CLI."""
    
    print("=" * 70)
    print("🤖 CHAT RAG - Sistema de Perguntas e Respostas sobre Documentos")
    print("=" * 70)
    print("\n💡 Dicas:")
    print("   - Digite sua pergunta e pressione Enter")
    print("   - Digite 'sair' ou 'exit' para encerrar")
    print("   - Digite 'limpar' ou 'clear' para limpar a tela")
    print("\n" + "=" * 70)

    llm = _build_llm()
    
    while True:
        try:
            # 1) Perguntar algo ao usuário no terminal
            print("\n📝 Sua pergunta:")
            pergunta = input("> ").strip()
            
            # Comandos especiais
            if pergunta.lower() in ['sair', 'exit', 'quit', 'q']:
                print("\n👋 Até logo!")
                break
            
            if pergunta.lower() in ['limpar', 'clear', 'cls']:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("=" * 70)
                print("🤖 CHAT RAG - Sistema de Perguntas e Respostas sobre Documentos")
                print("=" * 70)
                continue
            
            if not pergunta:
                print("⚠️  Por favor, digite uma pergunta.")
                continue
            
            # 2) Chamar a função search_documents
            print("\n🔍 Buscando documentos relevantes...")
            contexto = search_documents(pergunta)
            
            # 3) O contexto já está concatenado (search_documents retorna string)
            print("✓ Documentos encontrados!")
            
            # 4 e 5) Construir prompt e usar Google Gemini
            print("🤖 Gerando resposta com LLM...")
            resposta = ask_llm(llm, contexto, pergunta)
            
            # 6) Mostrar a resposta no terminal
            print("\n" + "=" * 70)
            print("💬 RESPOSTA:")
            print("=" * 70)
            print(resposta)
            print("=" * 70)
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrompido. Até logo!")
            break
        except ValueError as e:
            print(f"\n❌ Erro de configuração: {e}")
            print("\nVerifique se:")
            print("  1. O arquivo .env existe e contém GOOGLE_API_KEY")
            break
        except Exception as e:
            print(f"\n❌ Erro ao processar pergunta: {e}")
            print("\nVerifique se:")
            print("  1. O PostgreSQL está rodando (docker-compose up -d)")
            print("  2. A ingestão foi executada (python src/ingest.py)")
            print("  3. GOOGLE_API_KEY está configurada corretamente")
            print("\nTente novamente ou digite 'sair' para encerrar.")

if __name__ == "__main__":
    main()