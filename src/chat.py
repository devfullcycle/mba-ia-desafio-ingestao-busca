from search import search_prompt


def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Faça sua pergunta (ou 'sair' para encerrar):")
    while True:
        pergunta = input("PERGUNTA: ").strip()
        if pergunta.lower() in ("sair", "exit", "quit"):
            break
        if not pergunta:
            continue

        resposta = chain(pergunta)
        print(f"RESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()
