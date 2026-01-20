# Desafio MBA Engenharia de Software com IA - Full Cycle

Sistema RAG (Retrieval Augmented Generation) para ingestão e busca em documentos PDF usando PostgreSQL com pgvector.

## Funcionalidades

- Ingestão de documentos PDF em banco de dados vetorial
- Busca semântica usando embeddings
- Chat interativo para fazer perguntas sobre o documento
- Suporte para Google Gemini e OpenAI

## Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- Chave de API do Google Gemini ou OpenAI

## Configuração

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# API Keys (configure pelo menos uma)
GOOGLE_API_KEY=sua_chave_aqui
GOOGLE_EMBEDDING_MODEL=models/embedding-001
OPENAI_API_KEY=sua_chave_aqui
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Banco de dados
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=documentos

# Caminho do PDF
PDF_PATH=document.pdf
```

### 3. Iniciar o banco de dados

```bash
docker-compose up -d
```

Aguarde alguns segundos para o banco de dados inicializar e a extensão pgvector ser instalada.

## Uso

### Passo 1: Ingerir o documento PDF

```bash
python src/ingest.py
```

Este comando irá:
1. Carregar o PDF especificado em `PDF_PATH`
2. Dividir o documento em chunks de 1000 caracteres
3. Gerar embeddings usando Google Gemini ou OpenAI
4. Armazenar no PostgreSQL com pgvector

### Passo 2: Iniciar o chat

```bash
python src/chat.py
```

Agora você pode fazer perguntas sobre o documento:

```
============================================================
Chat RAG - Pergunte sobre o documento
============================================================
Digite 'sair' ou 'exit' para encerrar o chat

Inicializando sistema de busca...
✓ Sistema pronto!

Você: Qual é o tema principal do documento?
Buscando resposta...

Assistente: [resposta baseada no conteúdo do documento]

(Baseado em 4 trechos do documento)
```

## Estrutura do Projeto

```
.
├── src/
│   ├── ingest.py    # Ingestão de PDFs no banco vetorial
│   ├── search.py    # Sistema de busca RAG
│   └── chat.py      # Interface de chat interativa
├── document.pdf     # Documento de exemplo
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Tecnologias Utilizadas

- **LangChain**: Framework para aplicações com LLMs
- **PostgreSQL + pgvector**: Banco de dados vetorial
- **Google Gemini / OpenAI**: Modelos de embeddings e chat
- **PyPDF**: Carregamento de documentos PDF

## Troubleshooting

### Erro: "É necessário configurar GOOGLE_API_KEY ou OPENAI_API_KEY"
Configure pelo menos uma chave de API no arquivo `.env`.

### Erro: "PDF não encontrado"
Verifique se o caminho em `PDF_PATH` está correto no arquivo `.env`.

### Erro de conexão com banco de dados
Certifique-se de que o Docker está rodando:
```bash
docker-compose ps
docker-compose logs postgres
```