PROMPT_TEMPLATE = """
CONTEXTO:
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

def search_prompt(question=None):
  import os
  from dotenv import load_dotenv

  load_dotenv()

  DATABASE_URL = os.getenv("DATABASE_URL")
  EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
  LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-5-nano")

  if question is None:
    print("Nenhuma pergunta fornecida para search_prompt().")
    return None

  try:
    from langchain_openai import OpenAIEmbeddings, OpenAI
    from langchain_postgres import PGVector
    from langchain import LLMChain
    from langchain import PromptTemplate
  except Exception as e:
    print("Erro ao importar componentes do LangChain:", e)
    return None

  if not DATABASE_URL:
    print("DATABASE_URL não configurado. Defina a variável de ambiente.")
    return None

  embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

  try:
    # Tenta carregar store existente
    store = PGVector(table_name="documents", connection_string=DATABASE_URL, embeddings=embeddings)
  except Exception:
    try:
      store = PGVector.from_existing(table_name="documents", embeddings=embeddings, connection_string=DATABASE_URL)
    except Exception as e:
      print("Erro ao conectar ao PGVector store:", e)
      return None

  # Busca k=10
  try:
    results = store.similarity_search_with_score(question, k=10)
  except Exception as e:
    print("Erro durante a busca semântica:", e)
    return None

  # results -> list of (Document, score)
  contexto_parts = []
  for doc, score in results:
    text = getattr(doc, "page_content", str(doc))
    contexto_parts.append(text)

  contexto = "\n---\n".join(contexto_parts)

  prompt = PROMPT_TEMPLATE
  try:
    prompt_template = PromptTemplate(template=prompt, input_variables=["contexto", "pergunta"])
    llm = OpenAI(model_name=LLM_MODEL)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    resposta = chain.run({"contexto": contexto, "pergunta": question})
  except Exception as e:
    print("Erro ao chamar LLM:", e)
    return None

  if not resposta or resposta.strip() == "":
    return "Não tenho informações necessárias para responder sua pergunta."

  return resposta.strip()