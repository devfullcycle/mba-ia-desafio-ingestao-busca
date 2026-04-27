# PRD - Desafio Tecnico: Ingestao e Busca Semantica com LangChain e Postgres

## 1. Visao geral

Este projeto deve entregar uma aplicacao Python simples capaz de ingerir um arquivo PDF, armazenar seus embeddings em PostgreSQL com pgvector e responder perguntas via linha de comando com base apenas no conteudo do documento.

O foco e demonstrar a implementacao ponta a ponta de um fluxo basico de RAG para um desafio tecnico, com escopo reduzido e instrucoes claras de execucao.

## 2. Objetivo do produto

Permitir que uma pessoa:

- carregue um PDF local;
- processe e armazene seus trechos em um banco vetorial baseado em PostgreSQL + pgvector;
- faca perguntas em um chat de terminal;
- receba respostas fundamentadas somente no conteudo ingerido;
- receba uma resposta padrao quando a informacao nao estiver no contexto recuperado.

## 3. Problema

O desafio exige uma prova pratica de que o sistema consegue:

- ingerir conteudo nao estruturado em PDF;
- indexar semanticamente esse conteudo;
- recuperar os trechos mais relevantes;
- restringir a resposta da LLM ao contexto recuperado.

Sem isso, nao e possivel validar o uso correto de LangChain, banco vetorial e fluxo de pergunta e resposta.

## 4. Escopo

### Em escopo

- Ingestao de um unico arquivo `document.pdf`
- Divisao em chunks de 1000 caracteres com overlap de 150
- Geracao de embeddings
- Armazenamento no PostgreSQL com extensao pgvector
- Busca semantica com `k=10`
- Chat via CLI
- Resposta baseada apenas no contexto recuperado
- Resposta padrao para perguntas fora de contexto
- Documentacao de execucao no `README.md`
- Banco executado via Docker Compose

### Fora de escopo

- Interface web
- Upload de multiplos arquivos pelo usuario
- Painel administrativo
- Autenticacao e autorizacao
- Re-ranking avancado
- Memoria conversacional
- Citacao por pagina obrigatoria
- Observabilidade avancada
- Deploy em nuvem

## 5. Usuarios

### Usuario principal

Pessoa avaliadora ou recrutadora que quer executar o projeto localmente e validar o funcionamento do fluxo.

### Usuario secundario

Pessoa candidata que vai desenvolver, explicar e demonstrar a solucao.

## 6. Jornada principal

1. Usuario sobe o banco com `docker compose up -d`.
2. Usuario configura as variaveis de ambiente.
3. Usuario executa `python src/ingest.py`.
4. O sistema le `document.pdf`, quebra em chunks, gera embeddings e salva no banco.
5. Usuario executa `python src/chat.py`.
6. O sistema pede uma pergunta no terminal.
7. Usuario envia uma pergunta.
8. O sistema busca os 10 trechos mais relevantes.
9. O sistema monta o prompt com contexto e regras.
10. A LLM responde com base apenas no contexto.

## 7. Requisitos funcionais

FR-001: MUST - O sistema deve ler um arquivo PDF local chamado `document.pdf`
Acceptance Criteria:
- O arquivo deve ser lido a partir da raiz do projeto ou caminho esperado pela implementacao
- O processo deve falhar com mensagem clara se o arquivo nao existir
- O conteudo do PDF deve ser convertido em documentos processaveis

FR-002: MUST - O sistema deve dividir o conteudo do PDF em chunks de 1000 caracteres com overlap de 150
Acceptance Criteria:
- O splitter utilizado deve respeitar `chunk_size=1000`
- O splitter utilizado deve respeitar `chunk_overlap=150`
- Todos os chunks gerados devem ser encaminhados para a etapa de embeddings

FR-003: MUST - O sistema deve gerar embeddings para cada chunk
Acceptance Criteria:
- Cada chunk deve resultar em um vetor de embedding
- O provedor de embedding deve ser configurado por variavel de ambiente
- O processo deve falhar com mensagem clara se a chave de API nao estiver configurada

FR-004: MUST - O sistema deve armazenar os chunks e embeddings no PostgreSQL com pgvector
Acceptance Criteria:
- A conexao com o banco deve usar uma string de conexao configuravel por ambiente
- Os dados vetoriais devem ser persistidos em uma colecao acessivel para consulta posterior
- A ingestao concluida deve deixar os dados disponiveis para busca sem novo processamento

FR-005: MUST - O sistema deve permitir busca semantica a partir de uma pergunta do usuario
Acceptance Criteria:
- A pergunta deve ser convertida em embedding antes da busca
- A busca deve usar `similarity_search_with_score`
- A busca deve recuperar exatamente os 10 resultados mais relevantes quando disponiveis

FR-006: MUST - O sistema deve montar o contexto da resposta concatenando os resultados recuperados
Acceptance Criteria:
- Os documentos recuperados devem ser combinados em um bloco unico de contexto
- O prompt enviado para a LLM deve conter a secao `CONTEXTO`
- O prompt enviado para a LLM deve conter as regras obrigatorias fornecidas no desafio

FR-007: MUST - O sistema deve responder apenas com base no contexto recuperado
Acceptance Criteria:
- A resposta deve ser produzida a partir do prompt restritivo definido no desafio
- Se a informacao nao estiver explicitamente no contexto, a resposta deve ser a frase padrao exigida
- O sistema nao deve complementar a resposta com conhecimento externo

FR-008: MUST - O sistema deve oferecer uma interface CLI para perguntas e respostas
Acceptance Criteria:
- O script `src/chat.py` deve solicitar a pergunta no terminal
- O terminal deve exibir claramente `PERGUNTA:` e `RESPOSTA:`
- O usuario deve conseguir realizar pelo menos uma pergunta por execucao

FR-009: SHOULD - O sistema deve permitir escolher entre OpenAI e Gemini por configuracao
Acceptance Criteria:
- O provedor deve ser selecionavel sem alterar o codigo-fonte principal
- O modelo de embeddings deve seguir os nomes recomendados no desafio
- O modelo de LLM deve seguir os nomes recomendados no desafio

FR-010: SHOULD - O sistema deve exibir mensagens de erro simples e compreensiveis
Acceptance Criteria:
- Falta de API key deve gerar mensagem objetiva
- Falha de conexao com banco deve gerar mensagem objetiva
- Falha de ingestao deve encerrar o processo com indicacao do problema

## 8. Requisitos nao funcionais

NFR-001: MUST - O projeto deve ser executavel localmente com Python, Docker e Docker Compose

NFR-002: MUST - A estrutura do repositorio deve seguir exatamente o formato exigido no desafio

NFR-003: MUST - O README deve conter instrucoes suficientes para uma pessoa executar a solucao do zero

NFR-004: MUST - O sistema deve depender apenas das tecnologias obrigatorias ou recomendadas no desafio

NFR-005: SHOULD - A execucao de ingestao deve funcionar para um PDF simples sem exigir configuracao manual adicional no banco alem do `docker compose up -d`

NFR-006: SHOULD - O codigo deve ser pequeno, legivel e facil de avaliar em poucos minutos

## 9. Priorizacao MoSCoW

### Must Have

- Subir PostgreSQL com pgvector via Docker Compose
- Ler `document.pdf`
- Quebrar em chunks corretos
- Gerar embeddings
- Persistir embeddings no banco vetorial
- Buscar com `k=10`
- Montar prompt com contexto e regras obrigatorias
- Responder via CLI
- Retornar a frase padrao para fora de contexto
- Documentar a execucao

### Should Have

- Suporte configuravel a OpenAI e Gemini
- Mensagens de erro claras
- Codigo organizado em scripts simples e separados

### Could Have

- Comando de limpeza ou reinicializacao da colecao vetorial
- Exibicao opcional dos trechos recuperados para depuracao

### Won't Have

- Interface grafica
- Deploy em producao
- Historico de conversas
- Multiplos PDFs em uma mesma execucao

## 10. Epicos e historias

### Epico 1 - Preparacao do ambiente

Business Value: Permitir execucao local rapida e previsivel.

Historias:
- Como avaliador, quero subir o banco com um unico comando para validar o projeto rapidamente.
- Como desenvolvedor, quero configurar dependencias e variaveis de ambiente de forma simples para reduzir friccao.

### Epico 2 - Ingestao do documento

Business Value: Transformar o PDF em base consultavel por busca semantica.

Historias:
- Como usuario, quero processar um PDF local para disponibilizar seu conteudo no banco vetorial.
- Como usuario, quero que os chunks e embeddings sejam persistidos para nao depender do PDF durante a consulta.

### Epico 3 - Consulta e resposta via CLI

Business Value: Demonstrar a recuperacao semantica e o uso controlado da LLM.

Historias:
- Como usuario, quero fazer uma pergunta no terminal para obter uma resposta baseada no PDF.
- Como avaliador, quero ver o sistema recusando perguntas fora do contexto para confiar no comportamento esperado.

## 11. Dependencias e restricoes

### Dependencias

- Python
- PostgreSQL
- pgvector
- Docker e Docker Compose
- LangChain
- Provedor de LLM e embeddings com chave de API valida

### Restricoes

- O projeto deve seguir a estrutura obrigatoria definida no enunciado
- A execucao deve ocorrer por scripts Python simples
- A resposta deve usar somente o contexto recuperado
- O banco deve rodar localmente em container

## 12. Estrutura obrigatoria do repositorio

```text
repo/
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py
│   ├── search.py
│   └── chat.py
├── document.pdf
└── README.md
```

## 13. Criterios de sucesso

- Uma pessoa consegue subir o banco localmente sem ajustes manuais complexos
- A ingestao do PDF conclui com sucesso
- O chat responde perguntas que estejam claramente no PDF
- O chat retorna a frase padrao para perguntas fora de contexto
- O repositorio pode ser avaliado rapidamente por leitura do README e execucao de tres comandos

## 14. Criterios de aceite do produto

- `docker compose up -d` sobe o banco esperado
- `python src/ingest.py` processa o `document.pdf` e grava os embeddings
- `python src/chat.py` abre uma interacao de terminal
- Uma pergunta respondida explicitamente pelo PDF gera resposta coerente
- Uma pergunta sem suporte no contexto retorna:
  `Nao tenho informacoes necessarias para responder sua pergunta.`

## 15. Riscos

- Divergencias entre versoes de bibliotecas LangChain podem quebrar imports
- Configuracao incorreta de API keys pode impedir embeddings ou resposta
- PDF com texto ruim ou nao extraivel pode comprometer a qualidade da ingestao
- Busca semantica pode recuperar contexto insuficiente para perguntas ambiguas

## 16. Suposicoes

- O PDF fornecido contem texto extraivel
- O avaliador possui Docker funcional no ambiente
- O avaliador conseguira configurar ao menos um provedor de modelo
- O objetivo principal e clareza e funcionamento, nao sofisticacao arquitetural
