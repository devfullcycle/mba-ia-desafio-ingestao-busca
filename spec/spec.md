# **Ingestão e Busca Semântica com LangChain e Postgres**

## **Objetivo**

Você deve entregar um software capaz de:

1. **Ingestão:** Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão **pgVector**.  
2. **Busca:** Permitir que o usuário faça perguntas via **linha de comando (CLI)** e receba respostas baseadas apenas no conteúdo do PDF.

### **Exemplo no CLI**

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
**Faça sua pergunta:**

**PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?**  
**RESPOSTA: O faturamento foi de 10 milhões de reais.**

**\---**

**Perguntas fora do contexto:**

**PERGUNTA: Quantos clientes temos em 2024?**  
**RESPOSTA: Não tenho informações necessárias para responder sua pergunta.**  
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## **Tecnologias obrigatórias**

* **Linguagem:** Python  
* **Framework:** LangChain  
* **Banco de dados:** PostgreSQL \+ pgVector  
* **Execução do banco de dados:** Docker & Docker Compose (docker-compose fornecido no repositório de exemplo)

## **Pacotes recomendados**

* **Split:** `from langchain_text_splitters import RecursiveCharacterTextSplitter`  
* **Embeddings (OpenAI):** `from langchain_openai import OpenAIEmbeddings`  
* **Embeddings (Gemini):** `from langchain_google_genai import GoogleGenerativeAIEmbeddings`  
* **PDF:** `from langchain_community.document_loaders import PyPDFLoader`  
* **Ingestão**`from langchain_postgres import PGVector`  
* **Busca:** `similarity_search_with_score(query, k=10)`

## **Requisitos**

### **1\. Ingestão do PDF**

* O PDF deve ser dividido em **chunks de 1000 caracteres** com **overlap de 150**.  
* Cada chunk deve ser convertido em embedding.  
* Os vetores devem ser armazenados no banco de dados PostgreSQL com pgVector.

### **2\. Consulta via CLI**

* Criar um script Python para simular um chat no terminal.  
* Passos ao receber uma pergunta:  
  1. Vetorizar a pergunta.  
  2. Buscar os **10 resultados mais relevantes (k=10)** no banco vetorial.  
  3. Montar o prompt e chamar a LLM.  
  4. Retornar a resposta ao usuário.

### **Prompt a ser utilizado:**

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
**CONTEXTO:**  
**{resultados concatenados do banco de dados}**

**REGRAS:**  
**\- Responda somente com base no CONTEXTO.**  
**\- Se a informação não estiver explicitamente no CONTEXTO, responda:**  
  **"Não tenho informações necessárias para responder sua pergunta."**  
**\- Nunca invente ou use conhecimento externo.**  
**\- Nunca produza opiniões ou interpretações além do que está escrito.**

**EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:**  
**Pergunta: "Qual é a capital da França?"**  
**Resposta: "Não tenho informações necessárias para responder sua pergunta."**

**Pergunta: "Quantos clientes temos em 2024?"**  
**Resposta: "Não tenho informações necessárias para responder sua pergunta."**

**Pergunta: "Você acha isso bom ou ruim?"**  
**Resposta: "Não tenho informações necessárias para responder sua pergunta."**

**PERGUNTA DO USUÁRIO:**  
**{pergunta do usuário}**

**RESPONDA A "PERGUNTA DO USUÁRIO"**  
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## **Estrutura obrigatória do projeto**

| ├── docker-compose.yml ├── requirements.txt      \# Dependências ├── .env.example          \# Template da variável OPENAI\_API\_KEY ├── src/ │   ├── ingest.py         \# Script de ingestão do PDF │   ├── search.py         \# Script de busca │   ├── chat.py           \# CLI para interação com usuário ├── document.pdf          \# PDF para ingestão └── README.md             \# Instruções de execução  |
| :---- |

