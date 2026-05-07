from search import search_prompt

def main():
    print("=== Simulador de Chat ===")
    print("Digite sua pergunta ou 'sair' para encerrar.\n")

    while True:
        pergunta = input("Você: ")

        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("Encerrando o chat. Até mais!")
            break

        # Inicializa a cadeia de busca com a pergunta do usuário
        response = search_prompt(pergunta)

        if not response:
            print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
            continue

        # Executa a cadeia e mostra a resposta
        #resposta = chain.run(pergunta)
        print(f"Bot: {response}\n")

if __name__ == "__main__":
    main()