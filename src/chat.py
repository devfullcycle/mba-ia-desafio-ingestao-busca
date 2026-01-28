import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from search import similarity_search

PROMPT_TEMPLATE = """CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def build_context(results):
    partes = []
    for doc, score in results:
        partes.append(doc.page_content)
    return "\n\n---\n\n".join(partes)

def main():
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY não encontrada no .env")

    llm_model = os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash")
    llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0)

    print("Chat iniciado. (Ctrl+C para sair)\n")
    while True:
        pergunta = input("> ").strip()
        if not pergunta:
            continue

        resultados = similarity_search(pergunta, k=10)
        contexto = build_context(resultados)

        prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)
        resp = llm.invoke(prompt)
        print("\n" + resp.content.strip() + "\n")

if __name__ == "__main__":
    main()
