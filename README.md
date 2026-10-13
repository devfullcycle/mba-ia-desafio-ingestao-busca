# Ingestão e Busca Semântica com LangChain e Postgres

Sistema de RAG (Retrieval-Augmented Generation) que ingere um PDF em PostgreSQL com pgVector e responde perguntas via CLI, usando apenas o conteúdo do documento.

## Tecnologias

- Python 3 + LangChain
- PostgreSQL + pgVector (Docker Compose)
- Embeddings e LLM: OpenAI ou Google Gemini (selecionável via `.env`)

## Estrutura

```
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── document.pdf
├── src/
│   ├── ingest.py   # Ingestão do PDF (chunks + embeddings)
│   ├── search.py   # Busca semântica + chamada à LLM
│   └── chat.py     # CLI interativa
└── README.md
```

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- API Key da OpenAI **ou** do Google Gemini

## Configuração

1. Crie e ative o ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:

```bash
cp .env.example .env
```

Edite o `.env` e preencha a chave do provedor escolhido:

| Variável | Descrição |
|---|---|
| `EMBEDDING_PROVIDER` | `openai` ou `google` |
| `OPENAI_API_KEY` | Obrigatória se `EMBEDDING_PROVIDER=openai` |
| `OPENAI_EMBEDDING_MODEL` | Ex.: `text-embedding-3-small` |
| `OPENAI_CHAT_MODEL` | Ex.: `gpt-4o-mini` |
| `GOOGLE_API_KEY` | Obrigatória se `EMBEDDING_PROVIDER=google` |
| `GOOGLE_EMBEDDING_MODEL` | Ex.: `models/gemini-embedding-001` |
| `GOOGLE_CHAT_MODEL` | Ex.: `gemini-2.0-flash` |
| `DATABASE_URL` | URL do Postgres (padrão do compose) |
| `PG_VECTOR_COLLECTION_NAME` | Nome da collection no pgVector |
| `PDF_PATH` | Caminho do PDF a ingerir |

> **Atenção:** trocar o modelo de embeddings depois da ingestão exige recriar a collection (a dimensão do vetor muda). A ingestão já usa `pre_delete_collection=True` e recria a collection a cada execução.

## Execução

1. Suba o banco de dados:

```bash
docker compose up -d
```

2. Ingira o PDF:

```bash
python src/ingest.py
```

O script divide o PDF em chunks de 1000 caracteres (overlap 150), gera embeddings e grava no PGVector.

3. Inicie o chat:

```bash
python src/chat.py
```

Digite a pergunta no terminal. Use `sair`, `exit` ou `quit` para encerrar.

### Exemplo

```
Faça sua pergunta: Qual o faturamento da Empresa SuperTechIABrazil?
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.
```

Perguntas fora do contexto do PDF retornam:

```
Não tenho informações necessárias para responder sua pergunta.
```

## Como funciona

1. A pergunta é vetorizada com o mesmo modelo de embeddings da ingestão.
2. São buscados os 10 chunks mais similares (`k=10`) no pgVector.
3. O contexto recuperado monta o prompt enviado à LLM.
4. A resposta é gerada apenas com base nesse contexto.
