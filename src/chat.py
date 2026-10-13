from search import search_prompt


def main():
    print("---- Gustavo Chagas Bezerra ----")
    print("----- Iniciando CLI de chat -----")

    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("---- Chat pronto. Digite sua pergunta (sair/exit/quit para encerrar) ----")

    while True:
        print("----- Aguardando pergunta do usuário -----")
        try:
            question = input("Faça sua pergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n---- Encerrando chat ----")
            break

        if not question or question.lower() in {"sair", "exit", "quit"}:
            print("---- Encerrando chat ----")
            break

        print("----- Processando pergunta -----")
        answer = chain(question)

        print("---- Exibindo resposta ----")
        print(f"PERGUNTA: {question}")
        print(f"RESPOSTA: {answer}")
        print()


if __name__ == "__main__":
    main()
