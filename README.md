# Desafio MBA Engenharia de Software com IA - Full Cycle

## Configuração do Ambiente

1. **Criar e ativar um ambiente virtual (`venv`):**
   ```bash
   # Linux/Mac
   python3 -m venv venv && source venv/bin/activate

   # Windows
   python -m venv venv && venv\Scripts\activate
   ```

2. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuração das Variáveis de Ambiente**
   Criar o arquivo `.env` na raiz do projeto:
   ```env
   OPENAI_API_KEY=YOUR_OPENAI_KEY
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   DATABASE_URL=postgresql+psycopg://postgres:postgres@host.docker.internal:5432/rag
   PG_VECTOR_COLLECTION_NAME=desafio_rag_collection
   PDF_PATH=document.pdf
   ```

4. **Banco de Dados**
   Subir PostgreSQL + pgVector:
   ```bash
   docker compose up -d
   ```

5. **Processo de Ingestão**
   O script `ingest.py` lê o PDF, divide em chunks, gera embeddings e armazena no PostgreSQL com pgVector.
   ```bash
   python src/ingest.py
   ```

---

## Executando o Chat

```bash
python src/chat.py
```

Digite suas perguntas no prompt `PERGUNTA:` e `sair` para encerrar.

---

## Exemplos

### Pergunta presente no documento
```
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento da Empresa SuperTechIABrazil foi de 10 milhões de reais.
```

### Pergunta fora do contexto
```
PERGUNTA: Qual é a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

---

## Tecnologias Utilizadas

- Python
- LangChain
- PostgreSQL
- pgVector
- OpenAI
- Docker / Docker Compose
