from langchain_openai import ChatOpenAI

from search import search_prompt

def main():
    question = "Qual a capital da França" 
    chain = search_prompt(question)

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    GPT_NANO = "gpt-5-nano"
    llm = ChatOpenAI(model=GPT_NANO, temperature=0)

    new_chain = chain | llm

    result = new_chain.invoke({"pergunta":question})

    print(f"Pergunta: {question}")
    print(f"Resposta: {result.content}")

if __name__ == "__main__":
    main()