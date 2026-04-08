# Plano de Solução

## Criação dos Recursos

- [x] Criar chave OpenAI
- [x] Criação de chave no Google AI Studio
- [x] Subir banco localmente com o PGVector instalado


## Ingestão dos Dados

- [x] Ler pdf
- [x] Subdividir a informação do PDF em chunks com overlap
- [x] Configurar classe que realizará os embeddings
- [x] Instanciar store do banco
- [ ] Salvar embeddings e chunks no banco

## Criação da Busca

- [x] Configurar a classe de embbeding
- [x] Instanciar store do banco
- [x] Realizar busca com score no banco
- [x] Retornar consulta
- [ ] ~~Inserir gerenciamento de janela de contexto~~
- [x] Retornar chain

## Criação da Interface do Chatbot
- [x] Rodar interface
- [x] Instanciar Dependências
- [x] Delegar a busca
- [x] Resolver ciclo de conversa

