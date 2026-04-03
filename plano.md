# Plano de Solução

## Criação dos Recursos

- [ ] Criar chave OpenAI
- [ ] Criação de chave no Google AI Studio
- [ ] Subir banco localmente com o PGVector instalado



## Ingestão dos Dados

- [ ] Ler pdf
- [ ] Subdividir a informação do PDF em chunks com overlap
- [ ] Configurar classe que realizará os embeddings
- [ ] Instanciar store do banco
- [ ] Salvar embeddings e chunks no banco

## Criação da Busca

- [ ] Configurar a classe de embbeding
- [ ] Instanciar store do banco
- [ ] Realizar busca com score no banco
- [ ] Retornar consulta


## Criação da Interface do Chatbot
- [ ] Rodar interface
- [ ] Instanciar Dependências
- [ ] Delegar a busca
- [ ] Resolver ciclo de conversa

