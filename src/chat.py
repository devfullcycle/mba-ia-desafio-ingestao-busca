from search import search_prompt
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()
for k in ("OPENAI_API_KEY", "PGVECTOR_URL","PGVECTOR_COLLECTION"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

def main():
    while True:
        question = input("Digite sua pergunta: ")
        if question == "exit":
            break
        else:
            query = question
            embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))

            store = PGVector(
                embeddings=embeddings,
                collection_name=os.getenv("PGVECTOR_COLLECTION"),
                connection=os.getenv("PGVECTOR_URL"),
                use_jsonb=True,
            )

            results = store.similarity_search_with_score(query, k=10)
            contexto = "\n".join([f"Documento {i+1}: {doc.page_content.strip()}" for i, (doc, score) in enumerate(results)])
            chain = search_prompt(question=query, contexto=contexto)
            model = ChatOpenAI(model="gpt-5-nano", temperature=0.5)
            message = model.invoke(chain)

            print(message.content)
                        


if __name__ == "__main__":
    main()