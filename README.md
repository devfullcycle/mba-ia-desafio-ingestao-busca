# Desafio MBA Engenharia de Software com IA - Full Cycle

## Ingestão e Busca Semântica com LangChain e Postgres

Este projeto realiza ingestão de conteúdo de um arquivo PDF, armazena os vetores resultantes em um banco de dados vetorial e permite interagir com esse conteúdo por meio de um chat semântico.

### Funcionalidades principais
- Ingestão de texto a partir de PDF
- Criação de embeddings e armazenamento em banco vetorial
- Busca semântica de informações relevantes
- Interface de chat para consulta ao conteúdo ingerido

---

## VirtualEnv para Python
Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Ordem de execução
**1.** Subir o banco de dados:

```bash
docker compose up -d
```

**2.** Executar ingestão do PDF:

```bash
python src/ingest.py
```

**3.** Rodar o chat:

```bash
python src/chat.py
```

---

## Variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto ou em `src/.env` e defina as variáveis necessárias:

```dotenv
GOOGLE_API_KEY=<sua_chave_google>
OPENAI_API_KEY=<sua_chave_openai>
PGVECTOR_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5432/rag
GEMINI_MODEL=gemini-embedding-2-preview
PGVECTOR_COLLECTION=gemini_desafio_collection
PDF_PATH=document.pdf
```

- `GOOGLE_API_KEY`: chave de acesso à API Google.
- `OPENAI_API_KEY`: chave de acesso à API OpenAI.
- `PGVECTOR_URL`: URL de conexão com o banco de dados Postgres/Pgvector.
- `GEMINI_MODEL`: modelo de embeddings usado no projeto.
- `PGVECTOR_COLLECTION`: nome da coleção/índice no banco vetorial.
- `PDF_PATH`: caminho para o arquivo PDF que será ingerido.

---

## Observações
- Certifique-se de que o ambiente virtual esteja ativado antes de instalar dependências e executar os scripts.
- O arquivo `src/ingest.py` deve carregar e processar o PDF, salvando os vetores no banco.
- O arquivo `src/chat.py` abre um prompt de chat para fazer perguntas ao conteúdo ingerido.
