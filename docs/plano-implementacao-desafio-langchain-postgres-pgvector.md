# Phase 01 — RAG CLI com LangChain, PostgreSQL e pgvector

## Objective

Entregar o fluxo ponta a ponta de ingestao de `document.pdf`, indexacao vetorial em PostgreSQL com pgvector e consulta via CLI com respostas restritas ao contexto recuperado.

---

## Step Implementations

### SI-01.1 — Consolidar baseline de infraestrutura, configuracao e estrutura do projeto

**Description:** Ajustar o scaffold atual para uma base executavel e previsivel, corrigindo a infraestrutura local, centralizando configuracoes e preparando a estrutura minima para implementacao e testes.

**Technical actions:**

- Corrigir `docker-compose.yml` para manter apenas servicos validos e executaveis, alinhar o build do container de app com `Dockerfile.dev`, preservar o bootstrap da extensao `vector` e garantir dependencia explicita do PostgreSQL saudavel antes dos scripts Python.
- Criar um modulo de configuracao em `src/` para carregar `.env`, validar `DATABASE_URL`, `PDF_PATH`, `PG_VECTOR_COLLECTION_NAME`, `OPENAI_API_KEY`, `GOOGLE_API_KEY` e introduzir uma variavel de selecao de provedor (`LLM_PROVIDER`) com valores `openai` ou `gemini`.
- Atualizar `.env.example` com todas as variaveis realmente usadas pelo fluxo, incluindo os nomes de modelo de chat e embedding por provedor e valores default seguros para o ambiente local.
- Organizar o codigo em modulos reutilizaveis sem quebrar a estrutura obrigatoria do desafio, mantendo `src/ingest.py`, `src/search.py` e `src/chat.py` como pontos de entrada e extraindo utilitarios para arquivos como `src/config.py`, `src/providers.py` e `src/vectorstore.py`.
- Adicionar a base de testes do projeto com `pytest>=8,<9` e fixtures para ambiente/configuracao, preservando a simplicidade do repositorio.

**Tests:**

| File | Layer | Verifies |
|------|-------|----------|
| `tests/unit/test_config.py` | Unit | carregamento de configuracao, validacao de variaveis obrigatorias e mensagens de erro para ambiente invalido |
| `tests/integration/test_docker_compose_contract.py` | Integration | consistencia minima do contrato de infraestrutura local e presenca do bootstrap da extensao `vector` |

**Dependencies:** None

**Acceptance criteria:**

- `docker compose up -d` inicia o PostgreSQL local e aplica `CREATE EXTENSION IF NOT EXISTS vector` sem ajuste manual adicional.
- Executar qualquer script principal sem variaveis obrigatorias configuradas encerra o processo com mensagem objetiva indicando qual configuracao esta ausente.
- O projeto mantem os pontos de entrada `src/ingest.py`, `src/search.py` e `src/chat.py`, mas passa a reutilizar configuracoes e clientes compartilhados em modulos internos.

---

### SI-01.2 — Implementar abstracao de provedores de embeddings e LLM

**Description:** Criar a camada responsavel por selecionar OpenAI ou Gemini por configuracao, instanciando clientes de embeddings e de chat com APIs consistentes para o restante do fluxo.

**Technical actions:**

- Implementar uma factory de provedores em `src/providers.py` que selecione `langchain_openai.OpenAIEmbeddings` e `langchain_openai.ChatOpenAI` quando `LLM_PROVIDER=openai`, ou `langchain_google_genai.GoogleGenerativeAIEmbeddings` e `langchain_google_genai.ChatGoogleGenerativeAI` quando `LLM_PROVIDER=gemini`.
- Definir no modulo de configuracao quais variaveis de modelo devem ser lidas para cada provedor, incluindo `OPENAI_EMBEDDING_MODEL`, `OPENAI_CHAT_MODEL`, `GOOGLE_EMBEDDING_MODEL` e `GOOGLE_CHAT_MODEL`.
- Padronizar erros de inicializacao para cenarios de API key ausente, provedor invalido ou modelo nao configurado, retornando mensagens simples e adequadas ao uso em CLI.
- Expor funcoes reutilizaveis para obter o cliente de embeddings e o cliente de chat sem duplicar logica entre ingestao e consulta.

**Tests:**

| File | Layer | Verifies |
|------|-------|----------|
| `tests/unit/test_providers.py` | Unit | selecao correta do provedor, leitura de modelos por ambiente e erros de configuracao |
| `tests/unit/test_provider_errors.py` | Unit | mensagens de falha para API key ausente, provedor invalido e modelo nao definido |

**Dependencies:** SI-01.1

**Acceptance criteria:**

- Com `LLM_PROVIDER=openai`, a aplicacao inicializa clientes LangChain para OpenAI sem alterar codigo-fonte.
- Com `LLM_PROVIDER=gemini`, a aplicacao inicializa clientes LangChain para Gemini sem alterar codigo-fonte.
- Quando a API key exigida pelo provedor selecionado nao esta configurada, o processo falha com mensagem clara antes de iniciar ingestao ou chat.

---

### SI-01.3 — Implementar pipeline de ingestao do PDF no pgvector

**Description:** Construir o fluxo de leitura do PDF, fragmentacao em chunks, geracao de embeddings e persistencia no PostgreSQL usando `langchain-postgres`.

**Technical actions:**

- Implementar em `src/ingest.py` a leitura de `document.pdf` com `langchain_community.document_loaders.PyPDFLoader` ou loader equivalente baseado em `pypdf`, validando a existencia do arquivo em `PDF_PATH`.
- Dividir o conteudo com `langchain_text_splitters.RecursiveCharacterTextSplitter` configurado com `chunk_size=1000` e `chunk_overlap=150`, preservando metadados uteis como pagina e origem do arquivo.
- Criar um wrapper em `src/vectorstore.py` para instanciar `langchain_postgres.PGVector` com `connection=DATABASE_URL`, `collection_name=PG_VECTOR_COLLECTION_NAME`, `use_jsonb=True` e estrategia de criacao/abertura idempotente da colecao.
- Persistir os chunks com identificadores deterministas ou UUIDs, incluindo metadados minimos para rastreabilidade, e exibir resumo final de quantidade de paginas e chunks ingeridos.
- Tratar falhas de leitura do PDF, conexao com banco e escrita vetorial com mensagens compreensiveis e encerramento nao silencioso.

**Tests:**

| File | Layer | Verifies |
|------|-------|----------|
| `tests/unit/test_ingest_splitter.py` | Unit | aplicacao fixa de `chunk_size=1000` e `chunk_overlap=150` |
| `tests/unit/test_ingest_errors.py` | Unit | falhas de arquivo inexistente e dependencias de configuracao |
| `tests/integration/test_ingest_pgvector.py` | Integration | persistencia de documentos e embeddings na colecao configurada do PostgreSQL |

**Dependencies:** SI-01.1, SI-01.2

**Acceptance criteria:**

- `python src/ingest.py` com `document.pdf` presente processa o arquivo e persiste os chunks na colecao vetorial configurada.
- `python src/ingest.py` sem o arquivo configurado retorna erro explicito informando que o PDF nao foi encontrado.
- Ao final da ingestao, os dados ficam disponiveis para busca posterior sem novo processamento do documento.
- Se a conexao com o banco falhar, a execucao encerra exibindo uma mensagem objetiva sobre o problema de acesso ao PostgreSQL.

---

### SI-01.4 — Implementar busca semantica e montagem do prompt restritivo

**Description:** Construir a etapa de recuperacao semantica com `k=10`, consolidar o contexto textual e montar o prompt final que limita a resposta ao conteudo recuperado.

**Technical actions:**

- Implementar em `src/search.py` a abertura da mesma colecao `PGVector` criada na ingestao e a chamada `similarity_search_with_score(question, k=10)`.
- Normalizar os resultados recuperados em uma estrutura simples contendo texto, score e metadados relevantes para depuracao e composicao do contexto.
- Concatenar os textos recuperados em um bloco unico `CONTEXTO`, respeitando a ordem de relevancia retornada pela busca e preservando separadores claros entre trechos.
- Finalizar `PROMPT_TEMPLATE` com as regras obrigatorias do desafio e encapsular a chamada da LLM em uma funcao de servico que receba a pergunta e retorne resposta mais documentos recuperados.
- Implementar uma verificacao defensiva para contexto vazio ou insuficiente, mantendo a frase padrao `"Nao tenho informacoes necessarias para responder sua pergunta."` como fallback contratual.

**Tests:**

| File | Layer | Verifies |
|------|-------|----------|
| `tests/unit/test_search_prompt.py` | Unit | montagem do prompt com secao `CONTEXTO`, regras obrigatorias e pergunta do usuario |
| `tests/unit/test_search_fallback.py` | Unit | retorno da frase padrao quando nao ha contexto recuperado suficiente |
| `tests/integration/test_similarity_search.py` | Integration | uso de `similarity_search_with_score` com `k=10` e montagem do contexto a partir dos documentos retornados |

**Dependencies:** SI-01.2, SI-01.3

**Acceptance criteria:**

- Uma pergunta valida executa busca vetorial com `k=10` e monta um prompt contendo a secao `CONTEXTO` e as regras restritivas do desafio.
- Quando ha trechos aderentes no banco, a resposta da LLM e gerada a partir do contexto recuperado.
- Quando a informacao nao esta explicitamente presente no contexto recuperado, o sistema retorna exatamente `Nao tenho informacoes necessarias para responder sua pergunta.`

---

### SI-01.5 — Implementar a CLI de chat, fluxo de execucao e documentacao final

**Description:** Concluir a experiencia de uso do desafio com uma interface de terminal funcional, mensagens legiveis para a pessoa avaliadora e documentacao de execucao do zero.

**Technical actions:**

- Finalizar `src/chat.py` para solicitar a pergunta no terminal, exibir `PERGUNTA:` e `RESPOSTA:`, inicializar o servico de busca e tratar falhas de inicializacao de forma amigavel.
- Garantir que a execucao permita pelo menos uma pergunta por chamada do script, com opcao simples de encerrar por entrada vazia ou interrupcao do terminal.
- Adicionar um modo opcional de depuracao via variavel de ambiente para imprimir os trechos recuperados e scores sem poluir o fluxo padrao de avaliacao.
- Atualizar `README.md` com pre-requisitos, configuracao do `.env`, comandos de subida do banco, ingestao, chat e comportamento esperado para perguntas fora de contexto.
- Documentar no README a ordem recomendada de validacao manual do desafio e os comandos de teste automatizado do projeto.

**Tests:**

| File | Layer | Verifies |
|------|-------|----------|
| `tests/unit/test_chat_cli.py` | Unit | tratamento de pergunta vazia, falha de inicializacao e formatacao basica de saida |
| `tests/e2e/test_cli_flow.py` | E2E | fluxo completo `ingest.py` + `chat.py` em ambiente local com pergunta respondida e fallback fora de contexto |

**Dependencies:** SI-01.4

**Acceptance criteria:**

- `python src/chat.py` exibe `PERGUNTA:` no terminal e retorna `RESPOSTA:` para a entrada informada.
- Uma execucao bem-sucedida permite demonstrar pelo menos uma pergunta respondida com base no documento previamente ingerido.
- O `README.md` passa a permitir que uma pessoa rode o projeto do zero com `docker compose up -d`, `python src/ingest.py` e `python src/chat.py`.

---

## Technical Specifications

### Data Model

#### `langchain_pg_collection`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `uuid` | UUID | PK, generated | Identificador interno da colecao vetorial |
| `name` | string | unique, not null | Nome configurado por `PG_VECTOR_COLLECTION_NAME` |
| `cmetadata` | JSON | nullable | Metadados opcionais da colecao |

**Relations:** `langchain_pg_collection` -> `langchain_pg_embedding` (one-to-many)  
**Indexes:** unique (`name`)

---

#### `langchain_pg_embedding`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | string | PK | Identificador do chunk persistido |
| `collection_id` | UUID | FK -> `langchain_pg_collection.uuid`, on delete cascade | Liga o embedding a uma colecao |
| `embedding` | `vector` | not null | Vetor armazenado pelo `pgvector` |
| `document` | string | nullable | Conteudo textual do chunk |
| `cmetadata` | JSONB | nullable | Metadados como pagina, arquivo e ordem do chunk |

**Relations:** `langchain_pg_embedding` -> `langchain_pg_collection` (many-to-one)  
**Indexes:** GIN em `cmetadata`; indice vetorial gerenciado conforme estrategia adotada na implementacao do `PGVector`

---

### API Contracts

Nao se aplica nesta fase. O produto expoe apenas scripts CLI (`src/ingest.py` e `src/chat.py`) e nao endpoints HTTP.

---

### Events/Messages

Nao se aplica nesta fase. O fluxo e sincrono e local, sem filas ou mensageria.

## Dependency Map

```text
SI-01.1 (no deps)
└── SI-01.2
    └── SI-01.3
        └── SI-01.4
            └── SI-01.5
```

## Deliverables

- [ ] `docker-compose.yml` e `Dockerfile.dev` executam o ambiente local sem inconsistencias de caminho ou servicos
- [ ] Modulos compartilhados de configuracao, provedores e vector store adicionados em `src/`
- [ ] `src/ingest.py` processa `document.pdf`, gera embeddings e persiste os chunks no PostgreSQL com pgvector
- [ ] `src/search.py` executa busca semantica com `similarity_search_with_score` e `k=10`
- [ ] `src/chat.py` oferece a interacao CLI com resposta contextual e fallback padrao
- [ ] `README.md` documenta a execucao completa e o fluxo de validacao manual
- [ ] Testes passam (`pytest`)
- [ ] Verificacao de imports dos scripts principais passa (`python -m py_compile src/*.py`)
