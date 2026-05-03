# Desafio MBA Engenharia de Software com IA - Full Cycle

Este projeto implementa uma solução de ingestão e busca de documentos PDF utilizando LangChain, pgVector e PostgreSQL.

## Pré-requisitos

Para executar este projeto, você precisará das seguintes ferramentas instaladas:

- **Python 3.13+** (Recomendado utilizar [pyenv](https://github.com/pyenv/pyenv))
- **Docker** (v20.10+) e **Docker Compose** (v2.20+)
- **Chave de API**: [OpenAI](https://platform.openai.com/) ou [Google Gemini](https://aistudio.google.com/)

## Configuração do Ambiente

1. **Python**:
   Certifique-se de estar utilizando a versão correta do Python:
   ```bash
   python --version
   ```
   Se não estiver utilizando a versão correta, instale a versão correta do Python e crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Dependências**:
   Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

4. **Variáveis de Ambiente**:
   Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```
   Abra o arquivo `.env` e configure as seguintes variáveis:
   - **Chaves de API**: Adicione sua `OPENAI_API_KEY` ou `GOOGLE_API_KEY`.
   - **Configuração do Banco**: Com base no `docker-compose.yml`, utilize os seguintes valores:
     - `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag`
     - `PG_VECTOR_COLLECTION_NAME=pdf_chunks`
   - **Modelos e Arquivos**:
     - `GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001`
     - `GOOGLE_CHAT_MODEL=gemini-1.5-flash`
     - `PDF_PATH=document.pdf`

5. **Infraestrutura**:
   Suba o banco de dados PostgreSQL com pgVector:
   ```bash
   docker-compose up -d
   ```

## Como Executar

### 1. Ingestão de Dados
Certifique-se de que o banco de dados está rodando (`docker-compose up -d`) e então execute o script para processar o PDF e armazenar os vetores:
```bash
python src/ingest.py
```
*Nota: O script de ingestão agora processa os documentos em pequenos lotes com intervalos de tempo para evitar erros de cota (429) comuns no nível gratuito das APIs.*

### 2. Busca e Chat
Para iniciar o chat interativo no terminal e conversar com o conteúdo do PDF:
```bash
python src/chat.py
```
O chat buscará os 10 fragmentos mais relevantes do PDF para gerar cada resposta.
