# Desafio MBA Engenharia de Software com IA - Full Cycle

Projeto de RAG (ingestão de PDF + busca semântica com PGVector + resposta com Gemini).

## Pre-requisitos

- Python 3.10+
- Docker e Docker Compose
- Chave de API do Gemini (Google AI Studio)

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com:

```env
GOOGLE_API_KEY=sua_chave_gemini
PGVECTOR_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PGVECTOR_COLLECTION=documents
```

Observações:

- `PGVECTOR_COLLECTION` deve ser a mesma no `src/ingest.py` e no `src/chat.py`.
- O PDF usado na ingestão está em `./document.pdf`.

## Como rodar o projeto

1. Criar e ativar ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instalar dependências:

```bash
pip install -r requirements.txt
```

3. Subir banco PostgreSQL com pgvector:

```bash
docker compose up -d
```

4. Ingerir o PDF no banco vetorial:

```bash
python src/ingest.py
```

5. Iniciar o chat:

```bash
python src/chat.py
```

No chat, digite perguntas livremente. Para encerrar, digite `sair`.

## Solução de problemas rápida

- Erro `name ... violates not-null constraint`:
  - `PGVECTOR_COLLECTION` ausente no `.env`.
- Erro `DefaultCredentialsError`:
  - faltou `GOOGLE_API_KEY` no `.env`.
- Erro `429 Resource exhausted`:
  - limite de uso da API; aguarde e tente novamente.
- Resposta "Não tenho informações necessárias...":
  - resultado normal quando o contexto recuperado não contém a resposta explicitamente.
