# Desafio MBA Engenharia de Software com IA - Full Cycle

> Requer Python 3.11.9 para compatibilidade com as versões das dependências fixadas no requirements.txt.
> Configure o pyenv e garanta que a versão correta do Python esteja correta antes das etapas de setup abaixo.

Este é um pequeno laboratório RAG.

O projeto disponibiliza duas funcionalidades:

- Fazer a ingestão dos dados do PDF `document.pdf` como embeddings que são armazenados no PostgreSQL com pgvector.
- Responder perguntas do usuário baseado nos embeddings armazenados.

## Executando o projeto

Siga o passo a passo para fazer o setup e utilização do projeto.

### Setup

1. Criar ambiente para o projeto

python3 -m venv venv

2. Ativar o ambiente

source venv/bin/activate

3. Instalar as dependências

pip install -r requirements.txt

4. Subir o banco de dados:

docker compose up -d

### Ingestão

5. Executar ingestão do PDF:

python src/ingest.py

### Chat

6. Rodar o chat:

python src/chat.py
