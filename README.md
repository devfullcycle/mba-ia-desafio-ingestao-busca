# Desafio MBA Engenharia de Software com IA - Full Cycle

Este projeto implementa um sistema de Retrieval-Augmented Generation (RAG) para busca e resposta baseada em documentos PDF. Utiliza embeddings do Google Generative AI e armazenamento vetorial no PostgreSQL com pgVector.

## Funcionalidades

- **Ingestão de Documentos**: Carrega PDFs, divide em chunks e armazena embeddings vetoriais.
- **Busca Semântica**: Realiza buscas baseadas em similaridade vetorial.
- **Chat Interativo**: Interface de chat para perguntas e respostas baseadas no contexto dos documentos ingeridos.

## Arquitetura

- **Backend**: Python com LangChain
- **Embeddings**: Google Generative AI Embeddings
- **Banco de Dados**: PostgreSQL com pgVector
- **Containerização**: Docker Compose

## Pré-requisitos

- Docker e Docker Compose ([download](https://docs.docker.com/get-docker/))
- Chave da API do Google Generative AI ([obter aqui](https://aistudio.google.com/))
- Python 3.8+ ([download](https://python.org/downloads/))

## Configuração

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/caiojulian/mba-ia-desafio-ingestao-busca.git
   cd mba-ia-desafio-ingestao-busca
   ```

2. **Configure as variáveis de ambiente**:
   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_EMBEDDING_MODEL=models/embedding-001
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
   PG_VECTOR_COLLECTION_NAME=rag_collection
   PDF_PATH=path/to/your/document.pdf
   ```

3. **Inicie o banco de dados**:
   ```bash
   docker-compose up -d
   ```

4. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Linux/Mac
   # ou venv\Scripts\activate no Windows
   ```

5. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

## Como Usar

### 1. Ingerir Documentos

Execute o script de ingestão para carregar o PDF no banco vetorial:

```bash
python src/ingest.py
```

Este comando:
- Carrega o PDF especificado em `PDF_PATH`
- Divide o texto em chunks de 1000 caracteres com overlap de 150
- Gera embeddings para cada chunk
- Armazena os vetores no PostgreSQL

### 2. Executar o Chat

Inicie a interface de chat interativo:

```bash
python src/chat.py
```

Digite suas perguntas. O sistema buscará no contexto dos documentos ingeridos e fornecerá respostas baseadas apenas nas informações disponíveis.

Para sair, digite 'sair', 'quit' ou 'exit'.

## Estrutura do Projeto

```
.
├── docker-compose.yml          # Configuração do banco de dados
├── requirements.txt            # Dependências Python
├── src/
│   ├── chat.py                 # Interface de chat
│   ├── ingest.py               # Script de ingestão de documentos
│   └── search.py               # Lógica de busca e geração de respostas
└── README.md                   # Este arquivo
```

## Dependências Principais

- `langchain`: Framework para aplicações de IA
- `langchain-google-genai`: Integração com Google Generative AI
- `langchain-postgres`: Suporte ao PGVector
- `python-dotenv`: Gerenciamento de variáveis de ambiente
- `pypdf`: Carregamento de PDFs

## Notas

- As respostas são geradas estritamente baseadas no contexto dos documentos ingeridos.
- Se a pergunta não puder ser respondida com as informações disponíveis, o sistema informará que não tem informações necessárias.
- Certifique-se de que o banco de dados está rodando antes de executar ingestão ou chat.