from search import search_prompt


def main():

    print("=" * 60)
    print("CHAT RAG - PDF")
    print("Digite 'sair' para encerrar.")
    print("=" * 60)

    while True:

        pergunta = input("\nPERGUNTA: ").strip()

        if not pergunta:
            continue

        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("\nEncerrando chat...")
            break

        try:

            resposta = search_prompt.invoke(pergunta)

            print("\nRESPOSTA:")
            print(resposta)

        except Exception as ex:

            print("\nErro ao processar pergunta:")
            print(ex)


if __name__ == "__main__":
    main()