# Phase 01 — RAG CLI com LangChain, PostgreSQL e pgvector — Progress

**Status:** in_progress
**SIs:** 3/5 completed

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
- **Status:** pending
- **Tests:** pending
- **Observations:** none

### SI-01.5 — Implementar a CLI de chat, fluxo de execucao e documentacao final
- **Status:** pending
- **Tests:** pending
- **Observations:** none
