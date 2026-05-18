import argparse
from search import search_prompt


def main():
    parser = argparse.ArgumentParser(description="Chat CLI para consultar PDF ingerido.")
    parser.add_argument("--ingest", action="store_true", help="Executar ingestão antes de iniciar o chat")
    args = parser.parse_args()

    if args.ingest:
        try:
            from ingest import ingest_pdf
            print("Executando ingestão...")
            ingest_pdf()
        except Exception as e:
            print("Falha ao executar ingestão:", e)
            return

    print("Iniciando chat. Escreva 'sair' ou 'exit' para encerrar.")
    while True:
        try:
            pergunta = input("PERGUNTA: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando chat.")
            break

        if not pergunta:
            continue
        if pergunta.lower() in {"sair", "exit"}:
            print("Encerrando chat.")
            break

        resposta = search_prompt(pergunta)
        if not resposta:
            resposta = "Não tenho informações necessárias para responder sua pergunta."

        print("RESPOSTA:", resposta)


if __name__ == "__main__":
    main()