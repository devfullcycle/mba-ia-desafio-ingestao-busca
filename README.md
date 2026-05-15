# Ingestão e Busca Semântica com LangChain e Postgres

Sistema RAG que ingere um PDF no PostgreSQL (pgVector) e responde perguntas via CLI usando apenas o conteúdo do documento.

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- Chave de API do [Google AI Studio](https://aistudio.google.com/apikey) (Gemini) **ou** [OpenAI](https://platform.openai.com/api-keys)

## Estrutura

```
├── docker-compose.yml
├── requirements.txt
├── .env                  # Credenciais (não versionado)
├── document.pdf          # PDF para ingestão
├── src/
│   ├── config.py         # Configuração compartilhada (.env)
│   ├── ingest.py         # Ingestão do PDF
│   ├── search.py         # Busca vetorial + prompt + LLM
│   └── chat.py           # CLI
└── README.md
```

## Configuração

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crie o arquivo .env na raiz do projeto com suas chaves, por exemplo:
#   GOOGLE_API_KEY=sua_chave
#   LLM_PROVIDER=gemini
#   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
#   PDF_PATH=document.pdf
```

## Execução

### 1. Subir o banco

```bash
docker compose up -d
```

### 2. Ingerir o PDF

```bash
python src/ingest.py
```

A ingestão divide o PDF em chunks de **1000** caracteres com overlap de **150**, gera embeddings e grava no pgVector. No plano gratuito do Gemini, o processo pode levar ~2 minutos (throttle automático de requisições).

### 3. Chat no terminal

```bash
python src/chat.py
```

Exemplo:

```
PERGUNTA:  O que é o modelo VAE usado no relatório?

RESPOSTA: Foi desenvolvido um modelo generativo baseado em Variational Autoencoder (VAE) para a geração de espectros sintéticos de XRF, buscando preservar tanto a estrutura espectral quanto as propriedades estatísticas dos dados reais. A arquitetura do VAE foi definida com base em redes neurais densas, compostas por um encoder, um espaço latente e um decoder simétrico.
```

Perguntas sem resposta no PDF:

```
PERGUNTA: Quantos clientes temos em 2024?

RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

Digite `sair` para encerrar.

## Provedores

| Variável | Padrão (Gemini) | OpenAI |
|----------|-----------------|--------|
| `LLM_PROVIDER` | `gemini` | `openai` |
| Embeddings | `models/gemini-embedding-001` | `text-embedding-3-small` |
| LLM | `gemini-2.5-flash-lite` | `gpt-4o-mini` (configure `OPENAI_MODEL`) |

> O desafio cita `models/embedding-001`; na API atual do Google AI Studio use `models/gemini-embedding-001`.

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `GOOGLE_API_KEY` | Chave Gemini |
| `OPENAI_API_KEY` | Chave OpenAI |
| `LLM_PROVIDER` | `gemini` ou `openai` |
| `DATABASE_URL` | Conexão PostgreSQL |
| `PDF_PATH` | Caminho do PDF (padrão: `document.pdf`) |
| `EMBED_BATCH_SIZE` / `EMBED_BATCH_DELAY_SEC` | Controle de cota na ingestão |
