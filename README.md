# Desafio MBA Engenharia de Software com IA - Full Cycle

## 📋 Descrição

Sistema RAG (Retrieval-Augmented Generation) que permite fazer perguntas sobre documentos PDF usando:

- **LangChain** para processamento e orquestração
- **PostgreSQL + pgvector** para armazenamento vetorial
- **Google Gemini** para embeddings e LLM
- **Docker** para containerização

## 🏗️ Estrutura do Projeto

```
.
├── docker-compose.yml          # Configuração do PostgreSQL com pgvector
├── requirements.txt            # Dependências Python
├── .env.example               # Exemplo de variáveis de ambiente
├── document.pdf               # Arquivo PDF a ser processado (você deve adicionar)
├── README.md                  # Este arquivo
└── src/
    ├── ingest.py              # Script de ingestão (carrega e processa PDF)
    ├── search.py              # Lógica de busca vetorial e RAG
    └── chat.py                # Interface CLI para perguntas
```

## 🚀 Como Executar

### 1️⃣ Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.10 ou superior
- Chave de API do Google Gemini

### 2️⃣ Configuração

**Passo 1:** Clone o repositório e entre na pasta

**Passo 2:** Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

**Passo 3:** Edite o arquivo `.env` com as variaveis abaixo:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_documents
PDF_PATH=document.pdf
GOOGLE_API_KEY=sua-chave-aqui
GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001
```

**Passo 4:** Adicione seu arquivo PDF na raiz do projeto com o nome `document.pdf`

### 3️⃣ Instalação

**Inicie o banco de dados PostgreSQL:**

```bash
docker-compose up -d
```

**Instale as dependências Python:**

```bash
pip install -r requirements.txt
```

### 4️⃣ Ingestão do PDF

Execute o script de ingestão para processar o PDF:

```bash
python src/ingest.py
```

Este script irá:

- ✅ Carregar o arquivo PDF
- ✅ Dividir em chunks de 1000 caracteres com overlap de 150
- ✅ Gerar embeddings para cada chunk
- ✅ Salvar no PostgreSQL usando pgvector

### 5️⃣ Fazer Perguntas

Inicie o chat interativo:

```bash
python src/chat.py
```

**Comandos disponíveis no chat:**

- Digite sua pergunta e pressione Enter
- `sair` ou `exit` - Encerra o chat
- `limpar` ou `clear` - Limpa a tela

## 🔍 Como Funciona

1. **Ingestão (ingest.py)**:
   - Carrega o PDF usando PyPDFLoader
   - Divide em chunks de 1000 caracteres com overlap de 150
   - Gera embeddings usando Google (`models/embedding-001`)
   - Salva no PostgreSQL com extensão pgvector

2. **Busca e Resposta (search.py + chat.py)**:
   - Recebe a pergunta do usuário
   - Busca os 10 trechos mais relevantes usando similaridade vetorial
   - Usa esses trechos como contexto para o LLM
   - Gera resposta baseada APENAS no contexto

## ⚙️ Configurações Avançadas

Você pode personalizar no arquivo `.env`:

- `DATABASE_URL` - String de conexão do PostgreSQL
- `PG_VECTOR_COLLECTION_NAME` - Nome da coleção no banco
- `PDF_PATH` - Caminho do arquivo PDF
- `GOOGLE_EMBEDDING_MODEL` - Modelo de embeddings do Google

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **LangChain** - Framework para aplicações com LLM
- **PostgreSQL** - Banco de dados relacional
- **pgvector** - Extensão para busca vetorial
- **Google Gemini API** - Embeddings (`models/gemini-embedding-001`) e LLM (`gemini-2.5-flash-lite`)
- **Docker** - Containerização

## 📝 Observações

- O sistema responde APENAS com base no conteúdo do PDF
- Se a informação não estiver no documento, retorna "Não tenho informações necessárias"
- Use chunks de 1000 caracteres para balancear contexto e precisão
- Overlap de 150 caracteres garante continuidade entre chunks

## 🐛 Troubleshooting

**Erro de conexão com banco:**

```bash
docker-compose down
docker-compose up -d
```

**Erro de API key:**

- Verifique se a chave está correta no arquivo `.env`
- Certifique-se de que tem créditos na conta

**PDF não encontrado:**

- Adicione um arquivo `document.pdf` na raiz do projeto
- Ou configure o caminho correto em `PDF_PATH` no `.env`
