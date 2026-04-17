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