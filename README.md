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
│   ├── config.py        # Configurações centralizadas e rate limit
│   ├── ingest.py        # Script de ingestão do PDF
│   ├── search.py        # Busca vetorial e montagem do prompt
│   └── chat.py          # CLI para interação com usuário
├── document.pdf         # PDF para ingestão
└── README.md
```

### Controle de Rate Limit (API do Google)

O uso da cota gratuita da API do Google possui limitações restritas de tokens por minuto (TPM). Para evitar erros de limite excedido (como o status `429 Too Many Requests`) durante a ingestão do PDF e geração de embeddings em lotes, o sistema implementa um controle de taxa de envio.

As configurações que controlam esse mecanismo estão definidas em [src/config.py](file:///c:/DEV/FullCycle/desafios/mba-ia-desafio-ingestao-busca/src/config.py):
- **`RATE_LIMIT_TPM`** (`30_000`): Limite de tokens por minuto estipulado para a API.
- **`CHARS_PER_TOKEN`** (`2`): Fator de conversão aproximado de caracteres por token para estimar o tamanho do payload.
- **`SAFETY_MARGIN`** (`0.75`): Margem de segurança de 75% aplicada ao limite total do lote para evitar estouro acidental do limite estimado.