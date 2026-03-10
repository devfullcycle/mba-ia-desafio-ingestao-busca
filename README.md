# MBA IA — Desafio Ingestão e Busca

Projeto de **RAG (Retrieval-Augmented Generation)** que ingere um PDF em um banco vetorial (PostgreSQL + pgvector) e permite fazer perguntas sobre o conteúdo via chat.

## Estrutura

- **`src/ingest.py`** — Carrega o `document.pdf`, divide em chunks e grava no PGVector.
- **`src/search.py`** — Template do prompt para respostas baseadas apenas no contexto.
- **`src/chat.py`** — Chat interativo: busca por similaridade + resposta com LLM.

## Pré-requisitos

- Python 3.9+
- Docker e Docker Compose (para subir o banco)
- Chave da API OpenAI

## Iniciar o banco (Docker Compose)

Antes de rodar ingestão ou chat, suba o PostgreSQL com pgvector:

```bash
docker compose up -d
```

Aguarde o healthcheck (postgres + extensão vector).

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com:

```env
OPENAI_API_KEY=sua_chave
PGVECTOR_URL=postgresql://postgres:postgres@localhost:5432/rag
PGVECTOR_COLLECTION=nome_da_colecao
```

Opcional: `OPENAI_MODEL` (padrão: `text-embedding-3-small` para embeddings).

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

1. **Banco** — subir o PostgreSQL com pgvector (se ainda não estiver rodando):

```bash
docker compose up -d
```

2. **Ingestão** — rodar uma vez para popular o banco com o PDF:

```bash
python src/ingest.py
```

3. **Chat** — perguntas sobre o documento (digite `exit` para sair):

```bash
python src/chat.py
```
