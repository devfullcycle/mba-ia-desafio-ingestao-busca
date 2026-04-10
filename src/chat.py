from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from search import search_prompt
from config import Config


def create_llm():
    match Config.EMBEDDING_MODEL:
        case "open_ai":
            return ChatOpenAI(model=Config.OPENAI_LLM_MODEL, temperature=0)
        case "google":
            return ChatGoogleGenerativeAI(
                model=Config.GOOGLE_LLM_MODEL,
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0
            )
        case _:
            raise LookupError("Opção de embedding model inválida.")

def extract_response_text(result) -> str:
    if isinstance(result.content, list):
        return result.content[0].get('text', 'Sem resposta') if result.content else "Sem resposta"
    return result.content

def main():
    llm = create_llm()

    print("Chat iniciado. Digite 'sair' para encerrar.\n")

    while True:
        try:
            question = input("PERGUNTA: ").strip()

            if question.lower() in ("sair"):
                break

            if not question:
                continue

            chain = search_prompt(question) | llm
            result = chain.invoke({"pergunta": question})
            resposta = extract_response_text(result)
            print(f"RESPOSTA: {resposta}\n")

        except ValueError as e:
            print(e)


if __name__ == "__main__":
    main()