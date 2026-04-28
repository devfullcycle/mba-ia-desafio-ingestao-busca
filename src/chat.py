import os
from search import search_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
load_dotenv()


def main():
    store = PGVector(
        embeddings=GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview"),
        collection_name=os.getenv("PGVECTOR_COLLECTION"),
        connection=os.getenv("PGVECTOR_URL"),
        use_jsonb=True,
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.5)
    chain = search_prompt | llm

    print("Chat iniciado. Digite 'sair' para encerrar.")
    while True:
        query = input("\nSua pergunta: ").strip()
        if not query:
            print("Nenhuma pergunta informada.")
            continue
        if query.lower() in {"sair", "exit", "quit"}:
            print("Encerrando chat.")
            break

        results = store.similarity_search_with_score(query, k=10)
        parts = [doc.page_content for doc, score in results]
        contexto = "\n\n---\n\n".join(parts)

        result = chain.invoke({"context": contexto, "query": query})
        print(result.content)


if __name__ == "__main__":
    main()