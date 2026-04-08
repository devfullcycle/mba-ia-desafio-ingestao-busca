from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from search import search_prompt
from config import Config

def main():

    try:
        question = "Quais informações você pode me fornecer?" 
        chain = search_prompt(question)

        if not chain:
            print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
            return

        match Config.EMBEDDING_MODEL:
            case "open_ai":
                GPT_NANO = "gpt-5-nano"
                llm = ChatOpenAI(model=GPT_NANO, temperature=0)
            case "google":
                GIMINI = "gemini-2.5-flash-lite"
                llm = ChatGoogleGenerativeAI(
                    model= GIMINI,
                    google_api_key=Config.GOOGLE_API_KEY,
                    temperature=0.7
                )
            case _:
                raise LookupError("Opção de embedding model inválida.")
        
        new_chain = chain | llm

        result = new_chain.invoke({"pergunta":question})

        print(f"Pergunta: {question}")

        # Extrai o texto da resposta (formato varia entre OpenAI e Google)
        if isinstance(result.content, list):
            # Google Gemini retorna uma lista de dicionários
            resposta = result.content[0]['text'] if result.content else "Sem resposta"
        else:
            # OpenAI retorna string diretamente
            resposta = result.content

        print(f"Resposta: {resposta}")

    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()