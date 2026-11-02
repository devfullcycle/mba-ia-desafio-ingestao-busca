# Ingestao e busca semantica com LangChain e Postgres

Este projeto implementa um fluxo simples de RAG (Retrieval-Augmented Generation). Um arquivo PDF e carregado, dividido em trechos, convertido em embeddings e armazenado no PostgreSQL com pgVector. As perguntas sao respondidas a partir dos trechos recuperados.

## Tecnologias

- Python 3.10 ou superior
- LangChain
- PostgreSQL 17 com pgVector
- Docker Compose
- Embeddings locais, OpenAI ou Google Gemini

## Estrutura

```text
mba-ia-desafio-ingestao-busca/
├── .env.example          Modelo das variaveis de ambiente (copiar com o nome ".env" e preencher)
├── .gitignore             Arquivos ignorados pelo Git
├── docker-compose.yml     Banco PostgreSQL com pgVector
├── document.pdf           Documento usado na ingestao
├── README.md              Documentacao do projeto
├── requirements.txt       Dependencias Python
└── src/
    ├── chat.py            Interface de perguntas no terminal
    ├── ingest.py          Leitura do PDF e gravacao dos embeddings
    └── search.py          Busca vetorial e montagem do contexto
```

## Requisitos

Instale previamente:

- Python;
- Docker Desktop com o Docker Compose;
- Git, caso o projeto seja clonado.

O projeto precisa de acesso a uma API de embeddings. A opcao `gemini` e a configuracao atualmente usada nos testes, mas tambem existe suporte a OpenAI e a embeddings locais.

## 1. Obter o projeto

### Windows PowerShell

```powershell
git clone https://github.com/ViniAguiar1/mba-ia-desafio-ingestao-busca.git
Set-Location .\mba-ia-desafio-ingestao-busca
```

### Linux ou macOS

```bash
git clone https://github.com/ViniAguiar1/mba-ia-desafio-ingestao-busca.git
cd mba-ia-desafio-ingestao-busca
```

Se o projeto ja estiver no computador, entre diretamente na pasta correspondente.

## 2. Criar o ambiente virtual

### Windows PowerShell

```powershell
python -m venv .\venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

O comando `Set-ExecutionPolicy` vale somente para a sessao atual do PowerShell. Como alternativa, os executaveis dentro de `.\venv\Scripts\` podem ser usados sem ativar o ambiente.

### Linux ou macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalar as dependencias

### Windows PowerShell, Linux ou macOS

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No Linux ou macOS, use `python3` no lugar de `python` se essa for a configuracao do sistema.

## 4. Configurar o ambiente

Crie o arquivo `.env` a partir do modelo:

### Windows PowerShell

```powershell
Copy-Item .env.example .env
notepad .env
```

### Linux ou macOS

```bash
cp .env.example .env
nano .env
```

Configure as variaveis de acordo com o provedor escolhido:

```env
GOOGLE_API_KEY=sua_chave_google
GOOGLE_EMBEDDING_MODEL=gemini-embedding-001

OPENAI_API_KEY=sua_chave_openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_chunks_gemini
PDF_PATH=./document.pdf

EMBEDDING_PROVIDER=gemini
LOCAL_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

LLM_PROVIDER=gemini
GEMINI_CHAT_MODEL=gemini-3.8-flash
OPENAI_CHAT_MODEL=gpt-5-nano
DEBUG=0
```

Nao compartilhe o arquivo `.env` nem suas chaves de API. Para usar OpenAI, altere `EMBEDDING_PROVIDER` e `LLM_PROVIDER` para `openai`. Para usar embeddings locais, defina `EMBEDDING_PROVIDER=local`.

## 5. Iniciar o PostgreSQL

Execute na pasta do projeto:

```bash
docker compose up -d
docker compose ps
```

O servico `bootstrap_vector_ext` cria a extensao `vector` automaticamente depois que o PostgreSQL estiver pronto. Se precisar executar a criacao manualmente:

### Windows PowerShell, Linux ou macOS

```bash
docker exec -it postgres_rag psql -U postgres -d rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 6. Ingerir o PDF

### Windows PowerShell

Com o ambiente virtual ativado:

```powershell
python .\src\ingest.py
```

Sem ativar o ambiente:

```powershell
.\venv\Scripts\python.exe .\src\ingest.py
```

### Linux ou macOS

```bash
python src/ingest.py
```

O processo carrega o PDF, divide o texto em chunks de 1000 caracteres com sobreposicao de 150 e grava os embeddings na colecao configurada.

## 7. Testar a busca

O teste abaixo monta o prompt com os trechos encontrados. Ele nao chama o modelo de chat.

### Windows PowerShell

```powershell
$env:PYTHONPATH = "src"
@'
from search import search_prompt

prompt = search_prompt(
    "Qual o faturamento da Empresa SuperTechIABrazil?",
    k=3,
    debug=True,
)
print(prompt)
'@ | python -
```

### Linux ou macOS

```bash
PYTHONPATH=src python - <<'PY'
from search import search_prompt

prompt = search_prompt(
    "Qual o faturamento da Empresa SuperTechIABrazil?",
    k=3,
    debug=True,
)
print(prompt)
PY
```

## 8. Executar o chat

### Windows PowerShell

```powershell
python .\src\chat.py
```

Sem ativar o ambiente virtual:

```powershell
.\venv\Scripts\python.exe .\src\chat.py
```

### Linux ou macOS

```bash
python src/chat.py
```

Para encerrar, digite `sair`, `exit` ou `:q`.

O modo de depuracao e opcional. Para exibir os trechos recuperados, use:

```env
DEBUG=1
```

Para ocultar a lista `top-k`, use:

```env
DEBUG=0
```

A busca vetorial continua sendo executada nos dois casos.

## 9. Consultar os dados no PostgreSQL

Listar as tabelas:

```bash
docker exec -it postgres_rag psql -U postgres -d rag -c "\dt"
```

Contar os embeddings de uma colecao:

```bash
docker exec -it postgres_rag psql -U postgres -d rag -c "SELECT COUNT(*) FROM langchain_pg_embedding e JOIN langchain_pg_collection c ON c.uuid = e.collection_id WHERE c.name = 'pdf_chunks_gemini';"
```

Troque `pdf_chunks_gemini` pelo valor definido em `PG_VECTOR_COLLECTION_NAME`.

## 10. Perguntas para teste

Perguntas que podem ser respondidas com dados do PDF:

- Qual o faturamento da Empresa SuperTechIABrazil?
- Quando foi fundada a Empresa Beta Energia Industria?
- Quais empresas tem faturamento acima de R$ 1.000.000,00?
- Quais empresas foram criadas depois de 2000?

Perguntas sem resposta no documento devem receber a mensagem definida no prompt:

```text
Nao tenho informacoes necessarias para responder sua pergunta.
```

Exemplos de perguntas que devem retornar essa resposta:

- Qual e a capital da Franca?
- Quantos clientes temos em 2024?
- Voce considera o faturamento bom ou ruim?
- Qual sera o faturamento da empresa no proximo ano?

## Trocar o provedor de embeddings

Altere estas variaveis no `.env`:

```env
EMBEDDING_PROVIDER=openai
PG_VECTOR_COLLECTION_NAME=pdf_chunks_openai
```

ou:

```env
EMBEDDING_PROVIDER=gemini
PG_VECTOR_COLLECTION_NAME=pdf_chunks_gemini
```

Depois execute a ingestao novamente. Use uma colecao diferente para cada modelo, pois embeddings de modelos distintos podem ter dimensoes incompatíveis. A reingestao tambem deve ser planejada para evitar duplicacao de chunks.

## Autoria

Ana Beatriz Thomaz  
MBA em Engenharia de Software com IA — Full Cycle  
[DevAnaBea](https://github.com/DevAnaBea)
