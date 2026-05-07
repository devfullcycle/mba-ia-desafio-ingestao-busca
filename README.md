# Desafio MBA Engenharia de Software com IA - Full Cycle

Pré-requisitos:
 - Instale o python 3 (utilizei 3.14)
 - Ative o ambiente virtual do python (em venv\Scripts\activate -> .bat se for windows)
 - Instale as dependências através do "pip install -r requirements.txt"
 - Criar o arquivo .env baseado no .env.example e adicione a chave de api do gemini
 - Execute "docker-compose up -d" na raíz do diretório

Rodar:
1 - Ingestão do documento: python src/ingest.py
2 - Iniciar chat: python src/chat.py
