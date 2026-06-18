from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

from search import search_prompt

def main():
    print("Chat iniciado. Digite sua pergunta ou 'sair' para encerrar.")
    user_input = input("Você: ")

    while True:
        if not user_input.strip():
            print("Entrada vazia. Por favor, digite uma pergunta ou 'sair' para encerrar.")
            user_input = input("Você: ")
            continue

        if user_input.lower() in ("sair", "exit", "quit"):
            print("Encerrando o chat. Até mais!")
            break

        question_tamplate = search_prompt(question=user_input)

        gemini_model = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")

        result = gemini_model.invoke(question_tamplate)
        print(result.content)
        user_input = input("\nAjudo em algo mais? Caso contrário, digite 'sair' para encerrar.\nVocê: ")

if __name__ == "__main__":
    main()