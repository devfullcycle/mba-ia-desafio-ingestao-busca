import sys
from pathlib import Path

# Garante que imports locais funcionem independente de onde o script é chamado
sys.path.append(str(Path(__file__).parent))

from search import search_prompt


def main():
    """CLI interativo para perguntas sobre o PDF."""

    print("Inicializando o sistema de busca...")
    componentes = search_prompt()

    if not componentes:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    chain = componentes["chain"]
    buscar_contexto = componentes["buscar_contexto"]

    print("=" * 50)
    print("Chat com PDF - Digite 'sair' para encerrar")
    print("=" * 50)

    while True:
        try:
            print("\nFaça sua pergunta:\n")
            pergunta = input("PERGUNTA: ").strip()

            if not pergunta:
                continue

            if pergunta.lower() in ("sair", "exit", "quit"):
                print("Encerrando. Até logo!")
                break

            # Passo 1: Buscar contexto relevante no banco vetorial
            contexto = buscar_contexto(pergunta)

            # Passo 2: Invocar a chain (prompt + LLM)
            resposta = chain.invoke({
                "contexto": contexto,
                "pergunta": pergunta,
            })

            # Passo 3: Exibir resposta
            print(f"\nRESPOSTA: {resposta}")

        except KeyboardInterrupt:
            print("\n\nEncerrando. Até logo!")
            break
        except Exception as e:
            print(f"\nERRO ao processar pergunta: {e}")
            print("Tente novamente.\n")


if __name__ == "__main__":
    main()