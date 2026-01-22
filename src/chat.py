from search import search_prompt # Importa a função search_prompt do seu módulo search.py

def main():
    """
    Função principal para o CLI de chat com busca de documentos.
    """
    print("=" * 60)
    print("Bem-vindo ao Chat de Documentos!")
    print("Este assistente responde a perguntas com base nos seus documentos.")
    print("=" * 60)
    print("\nComo usar:")
    print("  - Digite sua pergunta e pressione Enter.")
    print("  - Para sair, digite 'sair' ou 'exit'.")
    print("-" * 60)

    while True:
        user_query = input("\nUser: ").strip()

        if user_query.lower() in ["sair", "exit"]:
            print("Saindo do chat. Até mais!")
            break

        if not user_query:
            print("Por favor, digite uma pergunta.")
            continue

        print("Buscando e processando sua pergunta...")
        try:
            response = search_prompt(user_query)
            print("Assistant:")
            print(response)
        except Exception as e:
            print(f"\nOcorreu um erro ao processar sua pergunta: {e}")
            print("Por favor, tente novamente ou reformule sua pergunta.")

if __name__ == "__main__":
    main()

