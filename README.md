# Desafio MBA Engenharia de Software com IA - Full Cycle
# Document Intelligence CLI

Este projeto é um CLI (Command Line Interface) para interagir com documentos usando IA, permitindo busca e chat baseados no conteúdo dos seus PDFs.

## Setup

Siga os passos abaixo para configurar e rodar o projeto.

### Pré-requisitos

*   **Docker e Docker Compose:** Necessário para rodar o banco de dados PostgreSQL com a extensão `pgvector`.
*   **Python 3.12.12:** A versão do Python utilizada no projeto. O `uv` tentará usar uma versão compatível instalada no seu sistema ou fará o download da versão mais recente se necessário.
*   **uv:** Um gerenciador de pacotes e ambientes virtuais para Python. Para mais detalhes, consulte a [documentação oficial do uv](https://docs.astral.sh/uv/).

### 1. Configuração do Ambiente

Crie um arquivo `.env` na raiz do projeto, **copiando o conteúdo de `.env.example`**, e preencha as variáveis de ambiente (especialmente sua chave `GOOGLE_API_KEY`):

```
GOOGLE_API_KEY="SUA_CHAVE_GOOGLE_AI_AQUI"
GOOGLE_EMBEDDING_MODEL="models/embedding-001"
GOOGLE_MODEL="gemini-2.5-flash-lite"
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/rag"
PG_VECTOR_COLLECTION_NAME="gpt5_collection"
PDF_PATH="document.pdf"
```

*   `GOOGLE_API_KEY`: Sua chave da API do Google AI Studio ou Google Cloud.
*   `GOOGLE_EMBEDDING_MODEL`: Modelo de embedding a ser utilizado (o padrão é `models/embedding-001`).
*   `GOOGLE_MODEL`: Modelo de chat a ser utilizado (o padrão é `gemini-2.5-flash-lite`).
*   `DATABASE_URL`: URL de conexão com o banco de dados PostgreSQL.
*   `PG_VECTOR_COLLECTION_NAME`: Nome da coleção no banco de dados para armazenar os embeddings.
*   `PDF_PATH`: Caminho para o arquivo PDF que será ingerido.

### 2. Rodar o Banco de Dados com Docker Compose

Inicie o contêiner do PostgreSQL com `pgvector` usando Docker Compose. O nome do serviço do banco de dados no `docker-compose.yml` é `postgres_rag`.

```bash
docker-compose up -d postgres
```

Este comando irá subir o serviço `postgres` em background. O serviço `bootstrap_vector_ext` será executado automaticamente para criar a extensão `vector` no banco de dados.

### 3. Instalação das Dependências

Utilize `uv` para criar um ambiente virtual com a versão específica do Python 3.12.12 e instalar as dependências do projeto.

```bash
uv venv --python 3.12.12
source .venv/bin/activate  # ou .venv\Scripts\activate para Windows
uv pip install -r requirements.txt
```

### 4. Ingestão do Documento PDF

Execute o script de ingestão para processar seu arquivo PDF e armazenar os embeddings no banco de dados vetorial.

```bash
python src/ingest.py
```

### 5. Iniciar o Chat CLI

Após a ingestão, você pode iniciar o aplicativo de chat:

```bash
python src/chat.py
```

Agora você pode interagir com o assistente de chat, que responderá a perguntas com base no conteúdo do seu documento PDF ingerido.
