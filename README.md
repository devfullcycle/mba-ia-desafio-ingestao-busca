# Desafio MBA Engenharia de Software com IA - Full Cycle

Este projeto implementa um chatbot baseado em RAG (Retrieval-Augmented Generation) que utiliza busca semântica em documentos PDF. O sistema realiza ingestão de documentos, armazena embeddings em banco vetorial PostgreSQL com PGVector e responde perguntas usando LLMs (OpenAI ou Google).

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.10 ou superior
- Docker e Docker Compose
- Git
- Uma chave de API da OpenAI ou Google AI Studio



## Subir o Banco Postgresql localmente

OBS: Perceba que, embora a porta utilizada para o banco não seja a padrão, essa porta padrão pode ser utilizada.

Para subir o banco de dados, basta executar o seguinte comando na raiz do repositório:

```shell
docker compose up -d
```

Caso queira confirmar a criação do banco e adição da extensão, utilize as credenciais presentes no .yaml do docker compose e conecte-se ao banco com o SGBD de sua preferência. Após isso, verifique se a extensão vector foi adicionada na seção de extensões.



> Este comando sobe os recursos configurados no docker-compose.yaml de modo detached, permitindo que o terminal não fique travado com a execução dos containers recém criados.

## Inicialização do Ambiente

Uma vez com a infra local funcional, inicialize um ambiente virtual para separar o ambiente de execução de código do ambiente do usuário. Deste modo, os pacotes e libs utilizadas ficarão contidos apenas neste ambiente, não afetando o sistema.

### Criar e Ativar o Ambiente Virtual

Para ativar, na raiz do repositório, execute:

``` shell
python3 -m venv .venv # usa o pacote venv para criar uma pasta .venv com os scripts necessários para ambiente virtual
sudo chmod +x .venv/bin/activate # Habilita operações de execução para o binário activate
source .venv/bin/activate # ativa o ambiente
```

Caso precise desativar o ambiente, basta rodar o seguinte comando no repositório:
``` shell
deactivate
```

### Instalar Dependências Python

Com o ambiente virtual ativado, instale todas as dependências necessárias:

```shell
pip install -r requirements.txt
```

Este comando instalará todas as bibliotecas necessárias, incluindo:
- LangChain para RAG e LLMs
- PyPDF2 para processamento de PDFs
- PGVector para busca vetorial
- OpenAI e Google AI SDKs

## Configuração das Variáveis de Ambiente

Antes de executar a ingestão, configure o arquivo `.env` baseado no `.env.example`:

1. Copie o arquivo de exemplo:
```shell
cp .env.example .env
```

2. Edite o arquivo `.env` e configure as seguintes variáveis:

**API Keys** (escolha uma ou ambas):
- `OPENAI_API_KEY`: Sua chave da OpenAI
- `GOOGLE_API_KEY`: Sua chave do Google AI Studio

**Configurações de Embedding**:
- `EMBEDDING_MODEL`: Escolha entre `"open_ai"` ou `"google"`
- Mantenha os modelos padrão ou ajuste conforme necessário

**Configurações do Banco de Dados**:
- `PGVECTOR_URL`: URL de conexão (padrão já configurada para o Docker local)
- `PG_VECTOR_COLLECTION_NAME`: Nome da coleção (padrão: `documents`)

**Configurações de Processamento**:
- `PDF_PATH`: Caminho para o PDF (padrão: `"./document.pdf"`)
- `CHUNK_SIZE`: Tamanho dos chunks em caracteres (padrão: `1000`)
- `CHUNK_OVERLAP`: Sobreposição entre chunks (padrão: `100`)

## Ingestão dos Dados

O Chatbot precisa de dados para realizar a busca. Os dados que serão utilizados estão na raiz do repositório, no arquivo `document.pdf`. Antes de realizar buscas, é necessário realizar a ingestão destes dados.

Com as variáveis de ambiente já configuradas (seção anterior), execute na raiz do repositório:

```shell
python src/ingest.py
```

Este processo irá:
1. Ler o documento PDF especificado em `PDF_PATH`
2. Dividir o texto em blocos (chunks) de tamanho `CHUNK_SIZE` com sobreposição de `CHUNK_OVERLAP`
3. Gerar embeddings vetoriais para cada chunk usando o modelo configurado
4. Armazenar os chunks e seus embeddings no banco PostgreSQL com PGVector

Com isto, os blocos (chunks) serão criados e salvos no banco com seus vetores de embedding, permitindo a busca semântica por meio do cálculo de similaridade entre vetores.

## Utilização do Chatbot

Com a ingestão completa, você pode fazer perguntas sobre o conteúdo do documento.

### Executar o Chatbot

Execute o seguinte comando na raiz do repositório:

```shell
python src/chat.py
```

### Como Funciona

O sistema opera da seguinte forma:
1. Recebe sua pergunta
2. Gera embedding da pergunta usando o mesmo modelo configurado
3. Busca no banco vetorial os chunks mais similares semanticamente
4. Usa os chunks recuperados como contexto para a LLM
5. A LLM gera uma resposta baseada no contexto encontrado

### Personalizar Perguntas

O arquivo [chat.py](src/chat.py) possui uma pergunta padrão definida. Para fazer outras perguntas:

**Opção 1**: Edite a variável `question` no arquivo [chat.py](src/chat.py)
```python
question = "Sua pergunta aqui"
```

**Opção 2**: Modifique o código para aceitar input do usuário ou argumentos de linha de comando

### Exemplos de Perguntas

Dependendo do conteúdo do seu documento, você pode fazer perguntas como:
- "Qual é o tema principal do documento?"
- "Explique o conceito de [tópico específico]"
- "Quais são as principais conclusões?"
- "Resuma a seção sobre [assunto específico]"

O sistema retornará respostas baseadas no contexto encontrado no documento PDF. 