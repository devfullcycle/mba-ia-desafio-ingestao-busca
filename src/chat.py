from search import search_prompt

def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Chat iniciado. Digite 'sair' para encerrar.\n")

    while True:
        question = input("Você: ").strip()
        if not question:
            continue
        if question.lower() in ("sair", "exit", "quit"):
            print("Encerrando chat.")
            break

        response = chain.invoke(question)
        print(f"\nAssistente: {response}\n")

if __name__ == "__main__":
    main()
