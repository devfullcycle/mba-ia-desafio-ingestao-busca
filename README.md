# Desafio MBA Engenharia de Software com IA - Full Cycle

CLI de RAG com ingestao de `document.pdf`, persistencia vetorial em PostgreSQL com `pgvector` e consulta contextual usando LangChain.

## Pre-requisitos

- Python 3.11+
- Docker Compose com acesso a imagens Docker
- Chave de API para o provedor escolhido em `LLM_PROVIDER`

## Configuracao

1. Crie um arquivo `.env` a partir de `.env.example`.
2. Preencha as variaveis obrigatorias:

```env
LLM_PROVIDER=openai
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=rag_document
PDF_PATH=document.pdf
DEBUG_RETRIEVED_CHUNKS=false

OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

GOOGLE_API_KEY=
GOOGLE_EMBEDDING_MODEL=models/embedding-001
GOOGLE_CHAT_MODEL=gemini-1.5-flash
```

3. Escolha um provedor:

- `LLM_PROVIDER=openai` exige `OPENAI_API_KEY`
- `LLM_PROVIDER=gemini` exige `GOOGLE_API_KEY`

## Instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Subir o PostgreSQL

```bash
docker compose up -d postgres bootstrap_vector_ext
```

O servico `bootstrap_vector_ext` executa `CREATE EXTENSION IF NOT EXISTS vector;` automaticamente antes do container da aplicacao depender do banco.

## Ingestao do PDF

Com `document.pdf` presente no caminho configurado em `PDF_PATH`, rode:

```bash
python3 src/ingest.py
```

Saida esperada:

```text
Ingestao concluida com sucesso: <paginas> paginas e <chunks> chunks persistidos.
```

## Chat CLI

Depois da ingestao, rode:

```bash
python3 src/chat.py
```

Fluxo esperado:

- O terminal exibe `PERGUNTA:`
- A resposta e impressa como `RESPOSTA: ...`
- Uma entrada vazia encerra o chat
- `Ctrl+C` ou EOF tambem encerram a sessao

Quando `DEBUG_RETRIEVED_CHUNKS=true`, a CLI imprime os trechos recuperados, scores e metadados logo abaixo da resposta.

## Perguntas fora de contexto

Se a informacao nao estiver explicitamente presente nos trechos recuperados do documento, a resposta contratual e:

```text
Nao tenho informacoes necessarias para responder sua pergunta.
```

## Ordem recomendada de validacao manual

1. Subir o banco com `docker compose up -d postgres bootstrap_vector_ext`
2. Confirmar as variaveis do `.env`
3. Rodar `python3 src/ingest.py`
4. Rodar `python3 src/chat.py`
5. Fazer uma pergunta coberta pelo documento
6. Fazer uma pergunta fora de contexto para validar o fallback

## Testes automatizados

Executar a suite completa:

```bash
python3 -m pytest
```

Verificar imports dos scripts principais:

```bash
python3 -m py_compile src/*.py
```
