from typing import Callable

from search import search_prompt


def run_chat_loop(chain: Callable[[str], str]) -> None:
    print("Faça sua pergunta (digite 'sair' para encerrar):\n")

    while True:
        try:
            pergunta = input("PERGUNTA: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando.")
            break

        if pergunta.lower() in ("sair", "exit", "quit"):
            print("Encerrando.")
            break

        if not pergunta:
            continue

        try:
            resposta = chain(pergunta)
        except Exception as exc:
            print(f"Erro ao processar a pergunta: {exc}\n")
            continue

        print(f"RESPOSTA: {resposta}\n")


def main() -> None:
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    run_chat_loop(chain)


if __name__ == "__main__":
    main()
