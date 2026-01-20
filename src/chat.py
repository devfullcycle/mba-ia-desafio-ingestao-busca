from search import search_prompt


def main():
    """
    Interface de chat interativa para fazer perguntas sobre o documento ingerido.
    """
    print("="*60)
    print("Chat RAG - Pergunte sobre o documento")
    print("="*60)
    print("Digite 'sair' ou 'exit' para encerrar o chat\n")

    try:
        # Inicializar a chain de RAG
        print("Inicializando sistema de busca...")
        chain = search_prompt()

        if not chain:
            print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
            return

        print("✓ Sistema pronto!\n")

        # Loop de chat
        while True:
            # Ler pergunta do usuário
            try:
                question = input("Você: ").strip()
            except EOFError:
                print("\nEncerrando chat...")
                break

            # Verificar se o usuário quer sair
            if question.lower() in ['sair', 'exit', 'quit', 'q']:
                print("Encerrando chat...")
                break

            # Ignorar perguntas vazias
            if not question:
                continue

            # Processar a pergunta
            try:
                print("\nBuscando resposta...\n")
                result = chain.invoke({"query": question})

                # Exibir a resposta
                print(f"Assistente: {result['result']}\n")

                # Opcionalmente, mostrar os documentos fonte
                if result.get('source_documents'):
                    print(f"(Baseado em {len(result['source_documents'])} trechos do documento)\n")

            except Exception as e:
                print(f"\nErro ao processar pergunta: {str(e)}\n")

    except Exception as e:
        print(f"\nErro ao inicializar o sistema: {str(e)}")
        print("Certifique-se de que:")
        print("1. O banco de dados está rodando (docker-compose up -d)")
        print("2. O PDF foi ingerido (python src/ingest.py)")
        print("3. As variáveis de ambiente estão configuradas (.env)")
        return

    print("\nAté logo!")


if __name__ == "__main__":
    main()