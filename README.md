# Desafio MBA Engenharia de Software com IA - Full Cycle

Ingestão e busca semântica com LangChain e PostgreSQL + pgVector.

O projeto lê um PDF, divide o conteúdo em chunks, gera os embeddings e os armazena
no pgVector. Depois disso, uma CLI recebe perguntas no terminal e responde
**exclusivamente** com base no que está no PDF — qualquer pergunta fora desse
conteúdo recebe a resposta padrão de recusa.

## Stack

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.12 |
| Framework | LangChain |
| Banco vetorial | PostgreSQL 17 + pgVector |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | OpenAI `gpt-5-nano` |
| Infraestrutura | Docker & Docker Compose |

## Pré-requisitos

- Python 3.12 ou superior
- Docker e Docker Compose
- Uma API Key da OpenAI com créditos disponíveis

## Como executar

### 1. Ambiente virtual e dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Variáveis de ambiente

Copie o template e preencha a sua chave da OpenAI:

```bash
cp .env.example .env
```

```dotenv
OPENAI_API_KEY=sua-chave-aqui
OPENAI_EMBEDDING_MODEL='text-embedding-3-small'
OPENAI_LLM_MODEL='gpt-5-nano'
DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/rag'
PG_VECTOR_COLLECTION_NAME='desafio_rag'
PDF_PATH='document.pdf'
```

`OPENAI_API_KEY` é a única variável sem valor padrão. O `.env` está no
`.gitignore` e nunca é versionado.

### 3. Subir o banco de dados

```bash
docker compose up -d
```

Aguarde o container `postgres_rag` ficar saudável. O serviço `bootstrap_vector_ext`
roda uma única vez e cria a extensão `vector` no banco `rag`.

### 4. Executar a ingestão do PDF

```bash
python src/ingest.py
```

Saída esperada:

```
Lendo /caminho/do/projeto/document.pdf...
Paginas lidas: 34
Chunks gerados: 67 (tamanho 1000, sobreposicao 150)
Recriando a colecao 'desafio_rag'...
Gerando embeddings e gravando no pgVector...
Ingestao concluida em 8.6s
```

A ingestão recria a coleção a cada execução, então rodar o comando várias vezes
não duplica chunks — a contagem no banco permanece 67.

### 5. Rodar o chat

```bash
python src/chat.py
```

```
Chat com o conteudo do PDF.
Digite sair, exit, quit ou Ctrl+D para encerrar.

Faça sua pergunta:
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: R$ 10.000.000,00 (2025).

Faça sua pergunta:
PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

## Estrutura do projeto

```
├── docker-compose.yml     # PostgreSQL 17 + pgVector
├── requirements.txt       # Dependências
├── .env.example           # Template das variáveis de ambiente
├── src/
│   ├── ingest.py          # Ingestão do PDF no banco vetorial
│   ├── search.py          # Busca por similaridade + geração da resposta
│   └── chat.py            # CLI de interação com o usuário
├── document.pdf           # PDF utilizado na ingestão
└── README.md
```

## Como funciona

**Ingestão** (`src/ingest.py`) — o `PyPDFLoader` extrai o texto página a página e o
`RecursiveCharacterTextSplitter` divide em chunks de **1000 caracteres com
sobreposição de 150**. A sobreposição garante que uma linha da tabela cortada na
fronteira de um chunk apareça inteira no chunk vizinho. Cada chunk vira um vetor
de 1536 dimensões, gravado no pgVector.

**Busca** (`src/search.py`) — a pergunta é vetorizada pelo **mesmo** modelo de
embeddings usado na ingestão (vetores de modelos diferentes não são comparáveis) e
o `similarity_search_with_score(pergunta, k=10)` recupera os 10 chunks mais
próximos. Os textos são concatenados no campo `{contexto}` do prompt e enviados ao
`gpt-5-nano`.

**Restrição ao contexto** — a garantia de que o modelo não inventa está no prompt,
usado exatamente como especificado no enunciado, incluindo os três exemplos de
pergunta fora do contexto. Nenhuma lógica reescreve a saída do modelo.

### Diagnóstico da recuperação

O `search.py` também roda direto, mostrando o que a busca recupera **sem chamar a
LLM**. Útil para distinguir um erro de recuperação (veio o chunk errado) de um erro
de geração (veio o chunk certo e o modelo não usou):

```bash
python src/search.py "Qual o faturamento da empresa SuperTechIABrazil?"
```

```
PERGUNTA: "Qual o faturamento da empresa SuperTechIABrazil?"
10 trechos recuperados (k=10):

[ 1] score=0.4541 pagina=26
     Suprema Atacado Indústria R$ 25.486.483,65 1958 Suprema Biotech...
[ 2] score=0.4652 pagina=2
     Azul Turismo LTDA R$ 3.816.747,30 2018 Beta Ambiental Serviços...
...
```

## Notas de implementação

**Escolha do provedor.** O enunciado permite OpenAI ou Gemini. A implementação usa
OpenAI com os modelos citados nominalmente no desafio: `text-embedding-3-small` e
`gpt-5-nano`.

**Temperatura do modelo.** O `gpt-5-nano` pertence à família de raciocínio do
GPT-5, que aceita apenas o valor padrão de temperatura e rejeita a requisição se
outro for informado. Por isso o `ChatOpenAI` é instanciado sem esse parâmetro, e a
fidelidade ao contexto fica a cargo do prompt.

**Correção no `docker-compose.yml`.** O serviço `bootstrap_vector_ext` encerrava
com código 0 sem criar a extensão `vector`. A causa era `entrypoint: ["/bin/sh",
"-c"]` combinado com um `command` em formato de string: o Compose divide a string
em tokens, então o `sh -c` recebia apenas `PGPASSWORD=postgres` como script — uma
atribuição de variável que retorna 0 — e o `psql` nunca era executado. O `command`
passou a ser uma lista de um item, que chega inteiro ao shell.

## Solução de problemas

| Sintoma | Causa provável |
| --- | --- |
| `A variavel de ambiente X nao esta definida no .env` | O `.env` não foi criado a partir do `.env.example`, ou a variável está vazia |
| `connection refused` na porta 5432 | O container não subiu: rode `docker compose up -d` e aguarde o healthcheck |
| `type "vector" does not exist` | A extensão não foi criada: rode `docker compose up bootstrap_vector_ext` |
| Respostas sempre com a frase de recusa | A ingestão não foi executada; confira a contagem com `docker exec postgres_rag psql -U postgres -d rag -c "SELECT count(*) FROM langchain_pg_embedding;"` |
| `429 You exceeded your current quota` | A API Key não tem créditos disponíveis |
