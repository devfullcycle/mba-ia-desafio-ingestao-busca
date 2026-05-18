# Desafio: Ingestão e Busca Semântica (LangChain + Postgres + pgvector)

Este projeto implementa uma pipeline RAG (Retrieval-Augmented Generation): ingerimos um PDF, indexamos seus trechos em um banco PostgreSQL com `pgvector` e expomos um CLI de chat que responde apenas com base no conteúdo do PDF.

Pré-requisitos
- Docker & Docker Compose
- Python 3.10+
- Chave de API OpenAI ou Google (opcional, mas necessária para gerar embeddings e respostas)

Instalação

1. Crie e ative um virtualenv:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Copie o arquivo de exemplo de variáveis de ambiente e preencha as chaves:

```bash
cp .env.example .env
# edite .env e preencha OPENAI_API_KEY ou GOOGLE_API_KEY e DATABASE_URL
```

Infra (Postgres + pgvector)

Suba o banco com Docker Compose:

```bash
docker compose up -d
```

Execução

- Ingestão do PDF (gera e persiste embeddings no Postgres):

```bash
python src/ingest.py
```

- Iniciar chat CLI (opcionalmente rodar ingest antes com `--ingest`):

```bash
python src/chat.py --ingest
python src/chat.py
```

Exemplo de uso no CLI

```
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

Observações
- O prompt força a LLM a responder somente com base no contexto recuperado do banco. Se nada relevante for encontrado, a resposta padrão será: "Não tenho informações necessárias para responder sua pergunta.".
- Ajuste modelos e chaves em `.env`.

Licença

Projeto entregue como exercício.