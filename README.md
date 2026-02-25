# Chat RAG com Busca Semântica

> Desafio MBA Engenharia de Software com IA — Full Cycle
> Pipeline de Retrieval-Augmented Generation (RAG) sobre documentos PDF, com suporte a OpenAI e Google Gemini.

---

## Visão Geral

Este projeto implementa um **chat RAG** (Retrieval-Augmented Generation) que:

1. **Ingest** um documento PDF, fragmenta o texto e armazena embeddings vetoriais no PostgreSQL (pgvector).
2. **Responde** perguntas em linguagem natural buscando os trechos mais relevantes do documento e gerando respostas fundamentadas exclusivamente no conteúdo indexado.
3. **Mantém histórico** de conversa por sessão, permitindo perguntas de acompanhamento contextuais.

### Modelos suportados

| Provider | Embedding | Chat / LLM |
|----------|-----------|------------|
| **OpenAI** | `text-embedding-3-small` (1 536 dims) | `gpt-4o-mini` (configurável) |
| **Google Gemini** | `gemini-embedding-001` (3 072 dims) | `gemini-2.5-flash` (configurável) |

> O sistema detecta automaticamente o provider correto na etapa de chat com base na dimensão dos vetores armazenados.

---

## Pré-requisitos

| Ferramenta | Versão mínima |
|------------|---------------|
| Python | 3.11+ |
| Docker + Docker Compose | 24+ |
| Chave de API OpenAI **ou** Google AI Studio | — |

---

## Estrutura do Projeto

```
.
├── docker-compose.yml      # PostgreSQL 17 + extensão pgvector
├── requirements.txt        # Dependências Python (pip)
├── .env.example            # Variáveis de ambiente necessárias
├── document.pdf            # PDF a ser indexado (substitua pelo seu)
└── src/
    ├── ingest.py           # Carrega e indexa o PDF no pgvector
    ├── search.py           # Busca semântica + cadeia RAG + histórico
    └── chat.py             # Interface de chat interativa (CLI)
```

---

## Instalação e Configuração

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd langchain_semantic_search
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
# Escolha OpenAI ou Google (ou ambos, mas use apenas um por vez no ingest)
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

GOOGLE_API_KEY=AIza...
GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001
GOOGLE_CHAT_MODEL=gemini-2.5-flash

# Banco de dados
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=minha_colecao

# Caminho para o PDF a ser indexado
PDF_PATH=document.pdf
```

> **Importante:** use o mesmo provider de embeddings no `ingest` e no `chat`. A troca de provider exige reindexar o documento.

### 3. Suba o banco de dados

```bash
docker compose up -d
```

O Compose inicializa o PostgreSQL 17 e ativa a extensão `vector` automaticamente.

### 4. Instale as dependências Python

```bash
pip install -r requirements.txt
```

---

## Uso

### Passo 1 — Indexar o documento (ingest)

Execute uma única vez (ou sempre que trocar o PDF ou o provider de embeddings):

```bash
cd src
python ingest.py
```

Você verá o menu abaixo — escolha o provider desejado:

```
Escolha o modelo de embeddings:
  1 - OpenAI  (text-embedding-3-small)
  2 - Gemini  (models/gemini-embedding-001)

Opção [1/2]:
```

O script fragmenta o PDF em chunks de 1 000 caracteres (overlap de 150), gera os embeddings e persiste no PostgreSQL.

---

### Passo 2 — Iniciar o chat RAG

```bash
cd src
python chat.py
```

O sistema detecta automaticamente o provider a partir dos embeddings armazenados e exibe o modelo ativo:

```
Modelo detectado: OpenAI  — embedding: text-embedding-3-small | chat: gpt-4o-mini
Chat RAG iniciado. Digite 'sair' para encerrar.

Você:
```

**Comandos do chat:**

| Comando | Ação |
|---------|------|
| Digite sua pergunta e pressione `Enter` | Obtém resposta baseada no documento |
| `sair` / `exit` / `quit` | Encerra o chat |
| `Ctrl + C` | Interrompe o chat |

> O assistente responde **somente** com base no conteúdo do documento indexado. Perguntas fora do escopo recebem a mensagem padrão: *"Não tenho informações necessárias para responder sua pergunta."*

---

## Exemplo de uso

<!-- Insira aqui uma print da tela do chat em funcionamento -->

---

## Arquitetura RAG

```
PDF
 └─► PyPDFLoader
       └─► RecursiveCharacterTextSplitter (1 000 chars / 150 overlap)
             └─► Embeddings (OpenAI ou Gemini)
                   └─► PGVector (PostgreSQL + pgvector)
                               │
                   Pergunta ───┘
                         └─► similarity_search (top-10)
                               └─► PromptTemplate (contexto + histórico)
                                     └─► LLM (GPT ou Gemini Flash)
                                           └─► Resposta
```

---

## Variáveis de Ambiente — Referência Completa

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `OPENAI_API_KEY` | Se usar OpenAI | Chave de API da OpenAI |
| `OPENAI_EMBEDDING_MODEL` | Não | Modelo de embedding OpenAI (padrão: `text-embedding-3-small`) |
| `OPENAI_CHAT_MODEL` | Não | Modelo de chat OpenAI (padrão: `gpt-4o-mini`) |
| `GOOGLE_API_KEY` | Se usar Gemini | Chave de API do Google AI Studio |
| `GOOGLE_EMBEDDING_MODEL` | Não | Modelo de embedding Gemini (padrão: `models/gemini-embedding-001`) |
| `GOOGLE_CHAT_MODEL` | Não | Modelo de chat Gemini (padrão: `gemini-2.5-flash`) |
| `DATABASE_URL` | **Sim** | Connection string PostgreSQL (formato SQLAlchemy) |
| `PG_VECTOR_COLLECTION_NAME` | **Sim** | Nome da coleção de vetores no banco |
| `PDF_PATH` | **Sim** (ingest) | Caminho para o arquivo PDF a indexar |

---

## Solução de Problemas

**`RuntimeError: Nenhum embedding encontrado. Execute o ingest primeiro.`**
→ Execute `python ingest.py` antes de iniciar o chat.

**Erro de conexão com o banco**
→ Verifique se o container está rodando com `docker compose ps` e se `DATABASE_URL` está correto.

**`RuntimeError: Dimensão desconhecida`**
→ O banco contém vetores de dimensão não reconhecida. Limpe a coleção e reindexe com OpenAI (1 536 dims) ou Gemini (3 072 dims).

**Respostas genéricas / fora do contexto**
→ Certifique-se de que o PDF correto foi indexado e de que `PG_VECTOR_COLLECTION_NAME` corresponde ao usado no ingest.
