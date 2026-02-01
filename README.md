# Desafio MBA Engenharia de Software com IA - Full Cycle

# PDF Ingestion + Semantic Search (LangChain + Postgres/pgvector)

Projeto do desafio: ingestão de um PDF, armazenamento em Postgres com pgvector e busca semântica via CLI.

## Requisitos

- Python 3.10+
- Docker + Docker Compose
- (Opcional) WSL2 no Windows

## Estrutura do projeto
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│ ├── ingest.py
│ ├── search.py
│ ├── chat.py
├── document.pdf
└── README.md


## 1 Subir o banco de dados (Postgres + pgvector)

Na raiz do projeto:
```bash
docker compose up -d
docker compose ps

docker compose exec postgres psql -U postgres -d postgres -c "CREATE DATABASE rag;"
docker compose exec postgres psql -U postgres -d rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 2 Configurar .env

GOOGLE_API_KEY=coloque_sua_key
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001
GEMINI_LLM_MODEL=gemini-2.5-flash
PGVECTOR_URL=postgresql+psycopg://postgres:postgres@localhost:5433/rag
PGVECTOR_COLLECTION=gpt5_collection
PDF_PATH=document.pdf

## 3 Instalar dependências
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4 Ingestão do PDF
```bash
python src/ingest.py
```

## 5 Rodar o Chat (CLI)
```bash
python src/chat.py
```

## 6 Consultar dados no banco (opcional)
```bash
docker compose exec postgres psql -U postgres -d rag
```

```sql
\dt
SELECT COUNT(*) FROM langchain_pg_embedding;
SELECT document FROM langchain_pg_embedding LIMIT 5;
```
