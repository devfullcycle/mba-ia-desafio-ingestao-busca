from search import search_prompt

def main():
    print("Faça sua pergunta:")
    print("Digite 'sair' para encerrar.")
    
    while True:
        question = input("\nPergunta: ").strip()
        
        if question.lower() in ['sair', 'quit', 'exit']:
            print("Encerrando o chat. Até logo!")
            break
        
        if not question:
            continue
            
        try:
            response = search_prompt(question)
            print(f"Resposta: {response}")
        except Exception as e:
            print(f"Erro: {e}")
            print("Verifique se o banco de dados está rodando e os documentos foram ingeridos.")

if __name__ == "__main__":
    main()