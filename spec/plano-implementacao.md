# Plano de Implementação: Ingestão e Busca Semântica com LangChain e Postgres

Este documento descreve as etapas técnicas para implementar o sistema de Ingestão de PDF e Busca Semântica via CLI, cumprindo rigorosamente as especificações do `spec.md`.

## Proposed Changes

### Arquivos de Configuração

#### [MODIFY] .env.example
Atualizar ou confirmar as chaves base.

#### [NEW] .env
Criarei um arquivo local `.env` configurado para testes assim que tivermos definido o provedor.

---

### Ingestão de Dados

#### [NEW] src/ingest.py
Este script fará o parsing do PDF e salvamento no PGVector.
- **Passo 1:** Carregar variáveis de ambiente com `python-dotenv`.
- **Passo 2:** Carregar o PDF usando `PyPDFLoader("document.pdf")`.
- **Passo 3:** Dividir o texto com `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)`.
- **Passo 4:** Instanciar o modelo de Embeddings do Google (`GoogleGenerativeAIEmbeddings`).
- **Passo 5:** Instanciar o VectorStore `PGVector` do `langchain_postgres`.
- **Passo 6:** Salvar os documentos vetorizados no banco utilizando `vectorstore.add_documents()`.

---

### Busca no Banco Vetorial

#### [NEW] src/search.py
Responsável por conectar ao PGVector e recuperar o contexto.
- **Passo 1:** Definir uma função `buscar_contexto(query: str)`.
- **Passo 2:** Instanciar Embeddings e o banco `PGVector`.
- **Passo 3:** Realizar a busca usando o método `similarity_search_with_score(query, k=10)`.
- **Passo 4:** Formatar os 10 resultados retornados, concatenando seus textos (conteúdos) e retornar como uma string única para o Chat.

---

### CLI e Chatbot

#### [NEW] src/chat.py
Interface do usuário e integração com o LLM LangChain.
- **Passo 1:** Entrar em um loop (ex: `while True`) simulando o CLI.
- **Passo 2:** Receber a entrada de usuário de forma similar ao exemplo: `PERGUNTA: `.
- **Passo 3:** Chamar `buscar_contexto()` importada do `search.py`.
- **Passo 4:** Inserir o resultado obtido na string de Prompt definida na especificação.
- **Passo 5:** Fazer a chamada para o Chat Model do Google (`ChatGoogleGenerativeAI`).
- **Passo 6:** Imprimir o resultado como `RESPOSTA: <resposta da LLM>`.

## Decisões Técnicas

1. **Escolha de LLM / Embeddings:** Foi definido pelo usuário o uso do provedor Google (`GoogleGenerativeAIEmbeddings` e `ChatGoogleGenerativeAI`).
2. **Formato do Connection String:** Foi confirmado o uso do formato padrão `postgresql+psycopg://` para o `DATABASE_URL`.

## Verification Plan

### Automated Tests
- Subir o contêiner `postgres_rag` com o comando `docker compose up -d`.
- Executar `python src/ingest.py` e verificar logs de sucesso (e observar se vetores parecem ser do tamanho correto no banco).

### Manual Verification
- Executar `python src/chat.py`.
- Fazer perguntas existentes no PDF e validar as respostas.
- Fazer perguntas fora de contexto (ex: "Qual é a capital da França?") para validar que a LLM respeita rigorosamente a restrição `"Não tenho informações necessárias para responder sua pergunta."`.
