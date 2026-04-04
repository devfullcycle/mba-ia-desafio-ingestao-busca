# Desafio MBA Engenharia de Software com IA - Full Cycle

Descreva abaixo como executar a sua solução.





## Subir o Banco Postgresql localmente

OBS: Perceba que, embora a porta utilizada para o banco não seja a padrão, essa porta padrão pode ser utilizada.

Para subir o banco de dados, basta executar o seguinte comando na raiz do repositório:

```shell
docker compose up -d
```

Caso queira confirmar a criação do banco e adição da exteção, utilize as credenciais presente do .yaml do docker compose e concte-se co banco dom o SGBD de sua prefência. Após isso, verifique se a extensão vecto foi adicionada na secção de estenções.



> Este comando sobre os recursos configurados no docker-compose.yaml de modo detached, permitindo que o terminal não fique travado com a execusão dos containers recém criados.

## Inicialização do Ambiente

Uma vez com a infra local funcional, inicialize um ambiente virtual para separar o ambiente de execução de código do ambiente do usuário. Deste modo, os pacotes e libs utilizadas ficarão contidos apenas neste ambente, não afetando o sistema.
Para ativar, na raiz do repositório, execute:

``` shell
python3 -m venv .venv # usa o pacote venv para criar uma pasta .venv com os scripts necessários para ambiente virtual
sudo chmod +x ./venv/bin/activate # Habilita operações de execução para o binário activate
source ./venv/bin/activate # ativa o ambiente
```

Caso precise desativar o ambiente, basta rodar o seguinte comando no repositório:
``` shell
deactivate
```

Rode o código ingest na raíz do repositório, lembrando que este o repósitório aut
