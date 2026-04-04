# Plano de Implementação: Ingestão e Busca Semântica com LangChain e Postgres

Este documento descreve **cada etapa técnica em detalhe** para implementar o sistema de Ingestão de PDF e Busca Semântica via CLI, cumprindo rigorosamente as especificações do `spec.md`.

> **Nota para o agente executor:** Este plano deve ser seguido sequencialmente. Cada seção contém o código exato a ser implementado. Não improvise APIs — use exatamente os imports e classes aqui descritos.

---

## Decisões Técnicas

| Decisão | Valor |
|---|---|
| Provedor LLM / Embeddings | Google Gemini (`langchain-google-genai`) |
| Modelo de Embeddings | `models/embedding-001` (768 dimensões) |
| Modelo de Chat (LLM) | `gemini-2.0-flash` |
| Vector Store | `PGVectorStore` + `PGEngine` (pacote `langchain-postgres>=0.0.14`) |
| Driver PostgreSQL | `psycopg` (psycopg3) — connection string: `postgresql+psycopg://` |
| Collection / Table Name | `document_embeddings` |

> [!IMPORTANT]
> O pacote `langchain-postgres` na versão 0.0.15 (presente no `requirements.txt`) **deprecou** a classe `PGVector` em favor de `PGVectorStore` + `PGEngine`. O plano original referenciava `PGVector` — isso foi corrigido. A spec menciona `from langchain_postgres import PGVector` como **recomendação**, mas a implementação correta usa a API moderna.

---

## Pré-requisitos

Antes de iniciar a codificação:

1. **Subir o banco de dados:**
   ```bash
   docker compose up -d
   ```
   Aguardar o healthcheck do `postgres_rag` e a execução do `bootstrap_vector_ext` (que cria a extensão `vector`).

2. **Criar o ambiente virtual e instalar dependências:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Configurar o `.env`** (vide seção abaixo).

---

## Proposed Changes

### 1. Arquivos de Configuração

#### [MODIFY] `.env.example`

Manter o template com todas as variáveis necessárias. Conteúdo final:

```env
GOOGLE_API_KEY=
GOOGLE_EMBEDDING_MODEL=models/embedding-001
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=document_embeddings
PDF_PATH=document.pdf
```

> [!NOTE]
> O `DATABASE_URL` deriva diretamente do `docker-compose.yml`: usuário `postgres`, senha `postgres`, banco `rag`, porta `5432`. O driver DEVE ser `psycopg` (não `psycopg2`).

#### [NEW] `.env`

Criar um arquivo `.env` copiando o `.env.example` e preenchendo `GOOGLE_API_KEY` com a chave real do usuário. As demais variáveis já possuem valores padrão. **Este arquivo NÃO deve ser commitado** (já está no `.gitignore`).

---

### 2. Ingestão de Dados

#### [MODIFY] `src/ingest.py`

Substituir o conteúdo do esqueleto existente pelo script completo de ingestão.

**Responsabilidades:**
- Carregar o PDF
- Dividir em chunks (1000 chars, 150 overlap)
- Gerar embeddings via Google
- Salvar no PostgreSQL + pgVector

**Código completo:**

```python
import os
import sys

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGEngine
from langchain_postgres.vectorstores import PGVectorStore

load_dotenv()

# --- Configuração via variáveis de ambiente ---
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "document_embeddings")
PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")

# Dimensão do modelo embedding-001 do Google
VECTOR_SIZE = 768


def ingest_pdf():
    """Carrega o PDF, divide em chunks, gera embeddings e salva no PGVector."""

    # Valida variáveis obrigatórias
    if not DATABASE_URL:
        print("ERRO: DATABASE_URL não configurada no .env")
        sys.exit(1)
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERRO: GOOGLE_API_KEY não configurada no .env")
        sys.exit(1)

    # Passo 1: Carregar o PDF
    print(f"Carregando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"  -> {len(documents)} páginas carregadas.")

    # Passo 2: Dividir em chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"  -> {len(chunks)} chunks gerados.")

    # Passo 3: Instanciar o modelo de embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    # Passo 4: Configurar o PGEngine e inicializar a tabela
    engine = PGEngine.from_connection_string(url=DATABASE_URL)
    engine.init_vectorstore_table(
        table_name=COLLECTION_NAME,
        vector_size=VECTOR_SIZE,
    )

    # Passo 5: Criar o VectorStore
    vector_store = PGVectorStore.create_sync(
        engine=engine,
        table_name=COLLECTION_NAME,
        embedding_service=embeddings,
    )

    # Passo 6: Salvar os chunks no banco
    print("Salvando embeddings no banco de dados...")
    vector_store.add_documents(chunks)
    print(f"  -> {len(chunks)} chunks salvos com sucesso!")


if __name__ == "__main__":
    ingest_pdf()
```

**Detalhes importantes para o agente executor:**
- A ordem dos passos é crítica: engine → init_table → create store → add_documents.
- `init_vectorstore_table` é idempotente (pode ser chamado múltiplas vezes sem erro).
- O `vector_size=768` corresponde ao modelo `embedding-001` do Google. Se mudar o modelo de embeddings, este valor deve ser atualizado.

---

### 3. Busca no Banco Vetorial

#### [MODIFY] `src/search.py`

Substituir o esqueleto existente. Este módulo faz duas coisas:
1. Busca os k=10 documentos mais similares no PGVector
2. Exporta uma função que retorna o contexto formatado e uma chain pronta para uso pelo `chat.py`

**Código completo:**

```python
import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGEngine
from langchain_postgres.vectorstores import PGVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- Configuração ---
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "document_embeddings")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")

# --- Prompt Template (conforme spec.md) ---
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


def _get_vector_store() -> PGVectorStore:
    """Instancia e retorna o PGVectorStore conectado ao banco."""
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    engine = PGEngine.from_connection_string(url=DATABASE_URL)
    vector_store = PGVectorStore.create_sync(
        engine=engine,
        table_name=COLLECTION_NAME,
        embedding_service=embeddings,
    )
    return vector_store


def buscar_contexto(query: str, k: int = 10) -> str:
    """
    Busca os k documentos mais similares à query no banco vetorial.
    Retorna os textos concatenados como uma string única.
    """
    vector_store = _get_vector_store()
    resultados = vector_store.similarity_search_with_score(query, k=k)

    # Cada resultado é uma tupla (Document, score)
    textos = [doc.page_content for doc, _score in resultados]
    return "\n\n".join(textos)


def search_prompt():
    """
    Retorna um dicionário com os componentes necessários para o chat:
    - 'llm': instância do ChatGoogleGenerativeAI
    - 'prompt': PromptTemplate configurado
    - 'buscar_contexto': função de busca

    Retorna None se houver erro de configuração.
    """
    if not DATABASE_URL:
        print("ERRO: DATABASE_URL não configurada no .env")
        return None
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERRO: GOOGLE_API_KEY não configurada no .env")
        return None

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
    )

    prompt = PromptTemplate(
        input_variables=["contexto", "pergunta"],
        template=PROMPT_TEMPLATE,
    )

    chain = prompt | llm | StrOutputParser()

    return {
        "chain": chain,
        "buscar_contexto": buscar_contexto,
    }
```

**Detalhes importantes para o agente executor:**
- `similarity_search_with_score` retorna tuplas `(Document, float)`.
- `temperature=0` garante respostas determinísticas e aderentes ao contexto.
- A chain usa LCEL (LangChain Expression Language): `prompt | llm | StrOutputParser()`.
- A função `search_prompt()` mantém a assinatura original importada pelo `chat.py`, mas agora retorna um dicionário com a chain e a função de busca.

---

### 4. CLI e Chatbot

#### [MODIFY] `src/chat.py`

Substituir o esqueleto existente pelo loop interativo completo.

**Código completo:**

```python
from search import search_prompt


def main():
    """CLI interativo para perguntas sobre o PDF."""

    print("Inicializando o sistema de busca...")
    componentes = search_prompt()

    if not componentes:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    chain = componentes["chain"]
    buscar_contexto = componentes["buscar_contexto"]

    print("=" * 50)
    print("Chat com PDF - Digite 'sair' para encerrar")
    print("=" * 50)

    while True:
        try:
            pergunta = input("\nFaça sua pergunta: ").strip()

            if not pergunta:
                continue

            if pergunta.lower() in ("sair", "exit", "quit"):
                print("Encerrando. Até logo!")
                break

            # Passo 1: Buscar contexto relevante no banco vetorial
            contexto = buscar_contexto(pergunta)

            # Passo 2: Invocar a chain (prompt + LLM)
            resposta = chain.invoke({
                "contexto": contexto,
                "pergunta": pergunta,
            })

            # Passo 3: Exibir resposta
            print(f"\nRESPOSTA: {resposta}")

        except KeyboardInterrupt:
            print("\n\nEncerrando. Até logo!")
            break


if __name__ == "__main__":
    main()
```

**Detalhes importantes para o agente executor:**
- O `chat.py` importa `search_prompt` do `search.py` (import relativo, ambos no mesmo diretório `src/`).
- O loop captura `KeyboardInterrupt` (Ctrl+C) para saída elegante.
- A formatação da saída segue o padrão da spec: `RESPOSTA: <texto>`.
- O invoke recebe um dicionário com as variáveis `contexto` e `pergunta`, que correspondem às variáveis do `PromptTemplate`.

---

### 5. Atualizar `.env.example`

#### [MODIFY] `.env.example`

Atualizar para conter os valores padrão corretos:

```env
GOOGLE_API_KEY=
GOOGLE_EMBEDDING_MODEL=models/embedding-001
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=document_embeddings
PDF_PATH=document.pdf
```

---

### 6. Atualizar README.md

#### [MODIFY] `README.md`

```markdown
# Desafio MBA Engenharia de Software com IA - Full Cycle

## Ingestão e Busca Semântica com LangChain e Postgres

### Pré-requisitos

- Python 3.10+
- Docker e Docker Compose
- Chave de API do Google (Gemini)

### Como executar

1. **Suba o banco de dados:**
   ```bash
   docker compose up -d
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o arquivo `.env`:**
   ```bash
   cp .env.example .env
   ```
   Edite o `.env` e preencha `GOOGLE_API_KEY` com sua chave.

5. **Execute a ingestão do PDF:**
   ```bash
   python src/ingest.py
   ```

6. **Inicie o chat:**
   ```bash
   python src/chat.py
   ```

### Estrutura do projeto

```
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py        # Script de ingestão do PDF
│   ├── search.py        # Busca vetorial e montagem do prompt
│   └── chat.py          # CLI para interação com usuário
├── document.pdf         # PDF para ingestão
└── README.md
```
```

---

## Resumo das Correções em Relação ao Plano Original

| # | Problema no Plano Original | Correção |
|---|---|---|
| 1 | Referenciava `PGVector` (deprecated na v0.0.15) | Usa `PGVectorStore` + `PGEngine` (API moderna) |
| 2 | Não especificava `vector_size` | Adicionado `vector_size=768` (modelo `embedding-001`) |
| 3 | Não detalhava imports nem código exato | Código completo e copy-paste-ready para cada arquivo |
| 4 | `search.py` não conectava ao banco vetorial | Implementa `_get_vector_store()` com conexão completa |
| 5 | `search.py` não montava o prompt com LangChain | Usa `PromptTemplate` + `ChatGoogleGenerativeAI` + `StrOutputParser` via LCEL |
| 6 | `chat.py` não tinha o loop interativo | Loop completo com captura de input, busca e invocação da chain |
| 7 | Não validava variáveis de ambiente | Validações com mensagens de erro claras no `ingest.py` e `search.py` |
| 8 | `DATABASE_URL` padrão não definido | Derivado do `docker-compose.yml`: `postgresql+psycopg://postgres:postgres@localhost:5432/rag` |
| 9 | Nenhuma instrução sobre o modelo de Chat | Especificado `gemini-2.0-flash` com `temperature=0` |
| 10 | `README.md` sem instruções de execução | README completo com passo-a-passo |

---

## Verification Plan

### Automated Tests

1. **Subir o contêiner:**
   ```bash
   docker compose up -d
   ```
   Verificar que `postgres_rag` está healthy:
   ```bash
   docker compose ps
   ```

2. **Testar a ingestão:**
   ```bash
   python src/ingest.py
   ```
   **Saída esperada:**
   ```
   Carregando PDF: document.pdf
     -> N páginas carregadas.
     -> M chunks gerados.
   Salvando embeddings no banco de dados...
     -> M chunks salvos com sucesso!
   ```

3. **Verificar dados no banco (opcional):**
   ```bash
   docker exec -it postgres_rag psql -U postgres -d rag -c "SELECT COUNT(*) FROM document_embeddings;"
   ```
   Deve retornar o número de chunks salvos.

### Manual Verification

4. **Testar o chat:**
   ```bash
   python src/chat.py
   ```
   - Fazer perguntas cujas respostas existam no PDF → espera-se resposta baseada no conteúdo.
   - Fazer perguntas fora de contexto (ex: "Qual é a capital da França?") → espera-se: `"Não tenho informações necessárias para responder sua pergunta."`
   - Digitar `sair` → espera-se encerramento limpo.

### Critérios de Aceitação

- [ ] `ingest.py` executa sem erros e salva chunks no banco.
- [ ] `chat.py` inicia e aceita perguntas em loop.
- [ ] Perguntas sobre o PDF retornam respostas corretas e contextualizadas.
- [ ] Perguntas fora de contexto retornam a mensagem padrão de recusa.
- [ ] O sistema usa **exatamente** `chunk_size=1000`, `chunk_overlap=150`, `k=10`.
- [ ] O prompt utilizado é **idêntico** ao definido na spec.
