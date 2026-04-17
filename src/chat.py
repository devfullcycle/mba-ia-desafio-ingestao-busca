import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from search import search_prompt

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "OPENAI").upper()


def _get_chat_model():
    if PROVIDER == "OPENAI":
        model = os.getenv("OPENAI_LLM_MODEL", "gpt-5-nano")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY nao configurada no .env")
        return ChatOpenAI(model=model, api_key=api_key)

    if PROVIDER == "GOOGLE":
        model = os.getenv("GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY nao configurada no .env")
        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)

    raise ValueError("PROVIDER invalido. Use OPENAI ou GOOGLE")

def main():
    try:
        chat_model = _get_chat_model()
    except Exception as exc:
        print(f"Erro ao iniciar modelo de chat: {exc}")
        return

    print("Chat de busca semantica iniciado. Pressione CTRL+C para sair.")
    while True:
        try:
            question = input("\nPergunta: ").strip()
            if not question:
                print("Digite uma pergunta valida.")
                continue

            prompt = search_prompt(question)
            response = chat_model.invoke(prompt)

            answer = getattr(response, "content", "")
            if isinstance(answer, list):
                answer = "\n".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in answer
                )
            print(f"\nResposta:\n{answer}")
        except KeyboardInterrupt:
            print("\nEncerrando chat...")
            break
        except Exception as exc:
            print(f"Erro ao processar pergunta: {exc}")

if __name__ == "__main__":
    main()