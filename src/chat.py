import os
from dotenv import load_dotenv

from search import search_prompt
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

def main():
    print("=== CHAT RAG (digite 'sair' para encerrar) ===\n")

    while True:
        pergunta = input("PERGUNTA: ")

        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("Encerrando chat...")
            break

        # 1. monta prompt com contexto do PGVector
        prompt = search_prompt(pergunta)

        if not prompt:
            print("Erro ao gerar contexto.\n")
            continue

        # 2. chama LLM
        response = llm.invoke(prompt)

        # 3. exibe resposta
        print("\nRESPOSTA:")
        print(response.content)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()