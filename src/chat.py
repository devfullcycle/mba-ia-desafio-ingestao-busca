# src/chat.py
import os
import re
from textwrap import dedent
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LLMs (se houver chave)
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# nossa busca vetorial
from search import similarity_search_with_score, PROMPT_TEMPLATE as SEARCH_PROMPT_TEMPLATE


def get_llm():
    """
    Retorna uma LLM se houver credenciais.
    Prioridade:
      1) LLM_PROVIDER=gemini (com GOOGLE_API_KEY)
      2) LLM_PROVIDER=openai (com OPENAI_API_KEY)
      3) fallback: qualquer uma que tenha chave
      4) None se não houver nenhuma
    """
    load_dotenv()
    provider = (os.getenv("LLM_PROVIDER") or "").lower()
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    openai_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-nano")
    gemini_model = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash-lite")

    # prioridade ao provider explícito
    if provider == "gemini" and google_key:
        return ChatGoogleGenerativeAI(model=gemini_model, google_api_key=google_key)
    if provider == "openai" and openai_key:
        return ChatOpenAI(model=openai_model, api_key=openai_key, temperature=0)

    # fallback automático
    if openai_key:
        return ChatOpenAI(model=openai_model, api_key=openai_key, temperature=0)
    if google_key:
        return ChatGoogleGenerativeAI(model=gemini_model, google_api_key=google_key)

    return None  # modo offline


def build_context(docs_with_scores):
    """Concatena os textos dos documentos recuperados para virar o CONTEXTO."""
    parts = []
    for doc, score in docs_with_scores:
        txt = (doc.page_content or "").strip()
        if txt:
            parts.append(txt)
    return "\n\n---\n\n".join(parts)


# Prompt EXACTO do desafio (vamos usar o mesmo do search.py)
PROMPT = PromptTemplate.from_template(dedent(SEARCH_PROMPT_TEMPLATE))


def rule_based_answer(context: str, question: str) -> str:
    """
    Modo OFFLINE (sem LLM):
    - Responde somente se achar uma evidência explícita no CONTEXTO.
    - Caso contrário, retorna a frase padrão do desafio.
    Heurísticas simples e conservadoras (nada de inventar).
    """
    not_enough = 'Não tenho informações necessárias para responder sua pergunta.'

    if not context.strip():
        return not_enough

    q_lower = question.lower()

    # 1) Se a pergunta contém 'faturamento' e um possível nome de empresa,
    #    tentamos extrair a linha correspondente do contexto com um valor "R$ ...".
    if "faturamento" in q_lower:
        # tenta capturar o nome após "da", "de", etc.
        m = re.search(r"faturamento.*?(empresa|da|de)?\s*([A-Za-z0-9_.\-]+)", question, re.IGNORECASE)
        company = None
        if m:
            company = m.group(2)

        lines = [ln.strip() for ln in context.splitlines() if ln.strip()]
        currency_pat = re.compile(r"R\$\s?[\d\.\,]+")  # ex.: R$ 10.000.000,00

        # se conseguiu identificar uma empresa, priorize linhas que contenham o nome
        if company:
            for ln in lines:
                if company.lower() in ln.lower() and currency_pat.search(ln):
                    # forma de resposta do exemplo do desafio
                    val = currency_pat.search(ln).group(0)
                    return f"O faturamento foi de {val.replace('R$','R$ ' ).strip()}."

        # se não achou a empresa, mas a pergunta pede 'faturamento',
        # procure por alguma linha com valor monetário (bem conservador)
        for ln in lines:
            mo = currency_pat.search(ln)
            if mo:
                val = mo.group(0)
                return f"O faturamento foi de {val.replace('R$','R$ ' ).strip()}."

        return not_enough

    # 2) Se a pergunta é obviously fora do contexto (exemplos do enunciado)
    out_examples = ["capital da frança", "quantos clientes temos em 2024", "você acha isso bom ou ruim"]
    if any(s in q_lower for s in out_examples):
        return not_enough

    # 3) fallback conservador
    return not_enough


def answer(question: str, k: int = 10, debug: bool = False) -> str:
    """
    - Busca top-k
    - Monta prompt
    - Usa LLM se houver credenciais; senão, modo offline conservador
    """
    results = similarity_search_with_score(question, k=k)

    if debug:
        print("\n[debug] top-k trechos recuperados:")
        for i, (doc, score) in enumerate(results, 1):
            print(f"#{i} score={score:.4f} | preview={doc.page_content[:120]!r}")

    context = build_context(results)
    llm = get_llm()

    if llm is None:
        # OFFLINE
        return rule_based_answer(context, question)

    # Com LLM (OpenAI/Gemini)
    chain = PROMPT | llm | StrOutputParser()
    return chain.invoke({"contexto": context, "pergunta": question})


def main():
    load_dotenv()
    print("Digite sua pergunta (ou 'sair' para encerrar).")
    while True:
        try:
            q = input("\nPERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break

        if q.lower() in {"sair", "exit", ":q"}:
            print("Saindo...")
            break

        resp = answer(q, k=10, debug=os.getenv("DEBUG", "0") == "1")
        print(f"RESPOSTA: {resp}")


if __name__ == "__main__":
    main()
