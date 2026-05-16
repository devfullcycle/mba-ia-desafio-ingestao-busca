# Desafio MBA Engenharia de Software com IA - Full Cycle

## Requisitos

- Python 3.10+
- Docker Desktop

## Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Copie o arquivo de variáveis de ambiente e preencha com suas chaves:
```bash
cp .env.example .env
```

Edite o `.env`:
```
OPENAI_API_KEY=sua_chave_aqui
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=documents
PDF_PATH=document.pdf
```

## Execução

### 1. Suba o banco de dados

```bash
docker compose up -d
```

### 2. Ingira o PDF

```bash
python src/ingest.py
```

Execute este passo apenas uma vez, ou novamente se o PDF for alterado.

### 3. Inicie o chat

```bash
python src/chat.py
```

Digite sua pergunta e pressione Enter. Para encerrar, digite `sair`.

## Observações

- O pipeline responde apenas com base no conteúdo do PDF informado em `PDF_PATH`.
- Para usar o Google Gemini no lugar do OpenAI, substitua `OPENAI_API_KEY` por `GOOGLE_API_KEY` no `.env` e atualize os imports em `src/ingest.py` e `src/search.py` conforme indicado nos comentários.