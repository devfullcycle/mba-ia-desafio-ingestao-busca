# Phase 01 — RAG CLI com LangChain, PostgreSQL e pgvector — Progress

**Status:** completed
**SIs:** 5/5 completed

### SI-01.1 — Consolidar baseline de infraestrutura, configuracao e estrutura do projeto
- **Status:** completed
- **Tests:** `python -m pytest tests/unit/test_config.py tests/integration/test_docker_compose_contract.py` -> passed (6 tests)
- **Observations:** none

### SI-01.2 — Implementar abstracao de provedores de embeddings e LLM
- **Status:** completed
- **Tests:** `python -m pytest tests/unit/test_providers.py tests/unit/test_provider_errors.py` -> passed (5 tests)
- **Observations:** none

### SI-01.3 — Implementar pipeline de ingestao do PDF no pgvector
- **Status:** completed
- **Tests:** `python -m pytest tests/unit/test_ingest_splitter.py tests/unit/test_ingest_errors.py tests/integration/test_ingest_pgvector.py` -> passed (4 tests) / skipped (1 integration test sem PostgreSQL acessivel no container)
- **Observations:** o teste de integracao com pgvector esta implementado, mas depende de um PostgreSQL disponivel em `DATABASE_URL`

### SI-01.4 — Implementar busca semantica e montagem do prompt restritivo
- **Status:** completed
- **Tests:** `python3 -m pytest tests/unit/test_search_prompt.py tests/unit/test_search_fallback.py tests/integration/test_similarity_search.py` -> passed (3 tests)
- **Observations:** a busca semantica foi validada por doubles em teste de integracao, mas a checagem real de conectividade com PostgreSQL permaneceu bloqueada neste workspace porque `docker` e `psql` nao estao disponiveis e `DATABASE_URL` nao esta configurada

### SI-01.5 — Implementar a CLI de chat, fluxo de execucao e documentacao final
- **Status:** completed
- **Tests:** `python3 -m pytest tests/unit/test_chat_cli.py tests/e2e/test_cli_flow.py` -> passed (4 tests)
- **Observations:** a CLI final foi validada localmente com testes unitarios e E2E simulados; a demonstracao manual com PostgreSQL real continua dependente de um ambiente com `docker compose` e `DATABASE_URL` disponiveis
