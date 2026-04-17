# Ingestao e Busca Semantica com LangChain + PostgreSQL (pgVector)

Projeto completo de RAG com PDF usando Python, LangChain e PostgreSQL com pgVector.

## Estrutura

```text
.
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py
│   ├── search.py
│   └── chat.py
├── document.pdf
└── README.md
```

## Funcionalidades

1. Ingestao:
- Le o arquivo `document.pdf`
- Divide em chunks de 1000 caracteres com overlap de 150
- Gera embeddings
- Salva no PostgreSQL com pgVector

2. Busca:
- Recebe pergunta via CLI
- Vetoriza pergunta
- Busca os 10 chunks mais relevantes (`k=10`)
- Usa os chunks como contexto para a LLM responder

## Tecnologias

- Python
- LangChain
- PostgreSQL + pgVector
- Docker + Docker Compose

## Configuracao de ambiente

1. Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

2. Configure as variaveis.

### Opcao OpenAI

```env
PROVIDER=OPENAI
OPENAI_API_KEY=<SUA_CHAVE>
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-5-nano
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_chunks
PDF_PATH=document.pdf
```

### Opcao Google

```env
PROVIDER=GOOGLE
GOOGLE_API_KEY=<SUA_CHAVE>
GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001
GOOGLE_LLM_MODEL=gemini-2.5-flash-lite
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_chunks
PDF_PATH=document.pdf
```

## Como rodar

Instale dependencias Python:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Suba o banco:

```bash
docker compose up -d
```

Habilite a extensao pgvector no banco:

```bash
docker exec -it postgres_rag psql -U postgres -d rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Execute ingestao:

```bash
python src/ingest.py
```

Inicie o chat:

```bash
python src/chat.py
```

## Fluxo interno

1. `src/ingest.py`
- Carrega PDF com `PyPDFLoader`
- Divide com `RecursiveCharacterTextSplitter`
- Gera embeddings conforme `PROVIDER`
- Persiste no `PGVector`

2. `src/search.py`
- Recebe query
- Executa `similarity_search_with_score(k=10)`
- Concatena os chunks em um contexto unico
- Monta prompt com regras estritas de resposta

3. `src/chat.py`
- Executa loop interativo na CLI
- Chama busca para montar o prompt
- Chama LLM escolhida por variavel de ambiente
- Exibe resposta

## Observacoes

- Garanta que `document.pdf` contenha os dados que deseja consultar.
- Se mudar `PG_VECTOR_COLLECTION_NAME`, rode nova ingestao.