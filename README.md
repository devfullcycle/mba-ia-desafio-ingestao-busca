# Desafio MBA Engenharia de Software com IA - Full Cycle

Ingestão e busca semântica de um PDF usando LangChain, PostgreSQL + pgVector e Google Gemini.

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Uma API Key do Google Gemini: https://aistudio.google.com/apikey

## Configuração

1. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Copie o arquivo de variáveis de ambiente e preencha `GOOGLE_API_KEY`:

   ```bash
   cp .env.example .env
   ```

## Execução

1. Suba o banco de dados (Postgres + pgVector):

   ```bash
   docker compose up -d
   ```

2. Execute a ingestão do PDF (`document.pdf`):

   ```bash
   python src/ingest.py
   ```

3. Rode o chat via CLI:

   ```bash
   python src/chat.py
   ```

   Digite suas perguntas sobre o conteúdo do PDF. Digite `sair` para encerrar.
