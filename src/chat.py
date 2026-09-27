from search import search_prompt


def main() -> None:
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

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

        resposta = chain(pergunta)
        print(f"RESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()
