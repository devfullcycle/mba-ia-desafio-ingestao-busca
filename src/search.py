"""Busca semantica no pgVector e geracao da resposta restrita ao contexto do PDF."""

import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

QUANTIDADE_DE_TRECHOS = 10
SEPARADOR_ENTRE_TRECHOS = "\n\n"


@dataclass(frozen=True)
class ConfiguracaoDeBusca:
    """Variaveis de ambiente necessarias para a busca, ja validadas."""

    url_do_banco: str
    nome_da_colecao: str
    modelo_de_embeddings: str
    modelo_de_linguagem: str

    @classmethod
    def a_partir_do_ambiente(cls) -> "ConfiguracaoDeBusca":
        return cls(
            url_do_banco=cls._obrigatoria("DATABASE_URL"),
            nome_da_colecao=cls._obrigatoria("PG_VECTOR_COLLECTION_NAME"),
            modelo_de_embeddings=cls._obrigatoria("OPENAI_EMBEDDING_MODEL"),
            modelo_de_linguagem=cls._obrigatoria("OPENAI_LLM_MODEL"),
        )

    @staticmethod
    def _obrigatoria(nome: str) -> str:
        valor = os.getenv(nome)
        if not valor:
            raise ValueError(f"A variavel de ambiente {nome} nao esta definida no .env")
        return valor


@dataclass(frozen=True)
class TrechoEncontrado:
    """Um chunk recuperado do banco vetorial, com sua distancia para a pergunta."""

    texto: str
    score: float
    pagina: int | None

    @classmethod
    def a_partir_do_resultado(
        cls, documento: Document, score: float
    ) -> "TrechoEncontrado":
        return cls(
            texto=documento.page_content,
            score=score,
            pagina=documento.metadata.get("page"),
        )


class BuscadorDeTrechos:
    """Recupera do pgVector os trechos mais proximos da pergunta."""

    def __init__(self, configuracao: ConfiguracaoDeBusca):
        self._banco = PGVector(
            embeddings=OpenAIEmbeddings(model=configuracao.modelo_de_embeddings),
            collection_name=configuracao.nome_da_colecao,
            connection=configuracao.url_do_banco,
            use_jsonb=True,
        )

    def buscar(self, pergunta: str) -> list[TrechoEncontrado]:
        resultados = self._banco.similarity_search_with_score(
            pergunta, k=QUANTIDADE_DE_TRECHOS
        )
        return [
            TrechoEncontrado.a_partir_do_resultado(documento, score)
            for documento, score in resultados
        ]


class RespondedorDePerguntas:
    """Monta o contexto com os trechos recuperados e pede a resposta ao modelo."""

    def __init__(self, buscador: BuscadorDeTrechos, modelo_de_linguagem: str):
        self._buscador = buscador
        self._cadeia = (
            PromptTemplate.from_template(PROMPT_TEMPLATE)
            | ChatOpenAI(model=modelo_de_linguagem)
            | StrOutputParser()
        )

    def responder(self, pergunta: str) -> str:
        trechos = self._buscador.buscar(pergunta)
        return self._cadeia.invoke(
            {"contexto": self._montar_contexto(trechos), "pergunta": pergunta}
        )

    @staticmethod
    def _montar_contexto(trechos: list[TrechoEncontrado]) -> str:
        return SEPARADOR_ENTRE_TRECHOS.join(trecho.texto for trecho in trechos)


def search_prompt(question=None) -> RespondedorDePerguntas:
    """Cria o respondedor pronto para uso; se `question` vier, ja responde a ela."""
    configuracao = ConfiguracaoDeBusca.a_partir_do_ambiente()
    respondedor = RespondedorDePerguntas(
        buscador=BuscadorDeTrechos(configuracao),
        modelo_de_linguagem=configuracao.modelo_de_linguagem,
    )
    if question:
        print(respondedor.responder(question))
    return respondedor


def _diagnosticar_recuperacao(pergunta: str) -> None:
    """Modo de diagnostico: mostra o que a busca recupera, sem chamar a LLM."""
    trechos = BuscadorDeTrechos(ConfiguracaoDeBusca.a_partir_do_ambiente()).buscar(
        pergunta
    )
    print(f'PERGUNTA: "{pergunta}"')
    print(f"{len(trechos)} trechos recuperados (k={QUANTIDADE_DE_TRECHOS}):\n")
    for posicao, trecho in enumerate(trechos, start=1):
        previa = " ".join(trecho.texto.split())[:150]
        print(f"[{posicao:2d}] score={trecho.score:.4f} pagina={trecho.pagina}")
        print(f"     {previa}...\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Uso: python src/search.py "sua pergunta"')
        raise SystemExit(1)
    _diagnosticar_recuperacao(" ".join(sys.argv[1:]))
