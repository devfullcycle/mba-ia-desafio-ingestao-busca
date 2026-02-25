from search import init_agent_from_db, search_prompt


def main():
    label = init_agent_from_db()
    print(f"Modelo detectado: {label}")
    print("Chat RAG iniciado. Digite 'sair' para encerrar.\n")

    try:
        while True:
            question = input("Você: ").strip()

            if not question:
                continue

            if question.lower() in ("sair", "exit", "quit"):
                break

            answer = search_prompt(question)
            print(f"\nAssistente: {answer}\n")
    except KeyboardInterrupt:
        pass

    print("\nEncerrando chat.")


if __name__ == "__main__":
    main()
