from search import search_prompt


def main():
    print("=== Busca semântica no documento ===")
    print("Digite sua pergunta sobre o documento (ou 'sair' para encerrar).\n")

    while True:
        pergunta = input("PERGUNTA: ").strip()
        if not pergunta:
            continue
        if pergunta.lower() in ("sair", "exit", "quit"):
            print("Até mais!")
            break

        try:
            resposta = search_prompt(pergunta)
        except Exception as erro:
            print(f"Erro ao buscar resposta: {erro}\n")
            continue

        print(f"RESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()
