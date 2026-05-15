from search import search_prompt


def main() -> None:
    print("Chat RAG — digite sua pergunta (ou 'sair' para encerrar)\n")

    while True:
        try:
            question = input("PERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if not question:
            continue
        if question.lower() in {"sair", "exit", "quit"}:
            break

        try:
            answer = search_prompt(question)
        except Exception as exc:
            print(f"\nRESPOSTA: Erro ao processar pergunta: {exc}")
            continue

        print(f"\nRESPOSTA: {answer}\n")
        print("---")


if __name__ == "__main__":
    main()
