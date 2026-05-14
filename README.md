# Desafio MBA Engenharia de Software com IA - Full Cycle

Ordem de execução:

1. Criar ambiente para o projeto

python3 -m venv venv

2. Ativar o ambiente

source venv/bin/activate

3. Instalar as dependências

pip install -r requirements.txt

4. Subir o banco de dados:

docker compose up -d

5. Executar ingestão do PDF:

python src/ingest.py

6. Rodar o chat:

python src/chat.py