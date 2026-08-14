"""Ingestao do PDF: le o documento, divide em chunks e grava os embeddings no pgVector."""

import os
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent

TAMANHO_DO_CHUNK = 1000
SOBREPOSICAO_ENTRE_CHUNKS = 150


@dataclass(frozen=True)
class ConfiguracaoDeIngestao:
    """Variaveis de ambiente necessarias para a ingestao, ja validadas."""

    caminho_do_pdf: Path
    url_do_banco: str
    nome_da_colecao: str
    modelo_de_embeddings: str

    @classmethod
    def a_partir_do_ambiente(cls) -> "ConfiguracaoDeIngestao":
        return cls(
            caminho_do_pdf=cls._caminho_do_pdf(),
            url_do_banco=cls._obrigatoria("DATABASE_URL"),
            nome_da_colecao=cls._obrigatoria("PG_VECTOR_COLLECTION_NAME"),
            modelo_de_embeddings=cls._obrigatoria("OPENAI_EMBEDDING_MODEL"),
        )

    @staticmethod
    def _obrigatoria(nome: str) -> str:
        valor = os.getenv(nome)
        if not valor:
            raise ValueError(f"A variavel de ambiente {nome} nao esta definida no .env")
        return valor

    @classmethod
    def _caminho_do_pdf(cls) -> Path:
        # Caminhos relativos no .env sao resolvidos a partir da raiz do projeto,
        # para que a ingestao funcione independente do diretorio de onde e chamada.
        caminho = Path(cls._obrigatoria("PDF_PATH"))
        if not caminho.is_absolute():
            caminho = RAIZ_DO_PROJETO / caminho
        if not caminho.is_file():
            raise FileNotFoundError(f"PDF nao encontrado em {caminho}")
        return caminho


class RepositorioVetorial:
    """Encapsula o pgVector, isolando o restante do codigo dos detalhes do banco."""

    def __init__(self, configuracao: ConfiguracaoDeIngestao):
        self._nome_da_colecao = configuracao.nome_da_colecao
        self._banco = PGVector(
            embeddings=OpenAIEmbeddings(model=configuracao.modelo_de_embeddings),
            collection_name=configuracao.nome_da_colecao,
            connection=configuracao.url_do_banco,
            use_jsonb=True,
        )

    def recriar_colecao(self) -> None:
        """Apaga e recria a colecao, garantindo que reingerir nao duplique chunks."""
        self._banco.delete_collection()
        self._banco.create_collection()

    def armazenar(self, documentos: list[Document]) -> None:
        self._banco.add_documents(documentos)

    @property
    def nome_da_colecao(self) -> str:
        return self._nome_da_colecao


class IngestorDePdf:
    """Orquestra o fluxo carregar paginas -> dividir em chunks -> armazenar."""

    def __init__(
        self,
        caminho_do_pdf: Path,
        repositorio: RepositorioVetorial,
        divisor: RecursiveCharacterTextSplitter,
    ):
        self._caminho_do_pdf = caminho_do_pdf
        self._repositorio = repositorio
        self._divisor = divisor

    def executar(self) -> None:
        inicio = time.perf_counter()

        paginas = self._carregar_paginas()
        print(f"Paginas lidas: {len(paginas)}")

        chunks = self._dividir_em_chunks(paginas)
        print(
            f"Chunks gerados: {len(chunks)} "
            f"(tamanho {TAMANHO_DO_CHUNK}, sobreposicao {SOBREPOSICAO_ENTRE_CHUNKS})"
        )

        print(f"Recriando a colecao '{self._repositorio.nome_da_colecao}'...")
        self._repositorio.recriar_colecao()

        print("Gerando embeddings e gravando no pgVector...")
        self._repositorio.armazenar(chunks)

        print(f"Ingestao concluida em {time.perf_counter() - inicio:.1f}s")

    def _carregar_paginas(self) -> list[Document]:
        print(f"Lendo {self._caminho_do_pdf}...")
        return PyPDFLoader(str(self._caminho_do_pdf)).load()

    def _dividir_em_chunks(self, paginas: list[Document]) -> list[Document]:
        chunks = self._divisor.split_documents(paginas)
        return [self._com_metadados_limpos(chunk) for chunk in chunks]

    @staticmethod
    def _com_metadados_limpos(chunk: Document) -> Document:
        """Remove metadados vazios que o PyPDFLoader traz e que so poluem o jsonb."""
        chunk.metadata = {
            chave: valor
            for chave, valor in chunk.metadata.items()
            if valor not in ("", None)
        }
        return chunk


def ingest_pdf() -> None:
    configuracao = ConfiguracaoDeIngestao.a_partir_do_ambiente()
    ingestor = IngestorDePdf(
        caminho_do_pdf=configuracao.caminho_do_pdf,
        repositorio=RepositorioVetorial(configuracao),
        divisor=RecursiveCharacterTextSplitter(
            chunk_size=TAMANHO_DO_CHUNK,
            chunk_overlap=SOBREPOSICAO_ENTRE_CHUNKS,
        ),
    )
    ingestor.executar()


if __name__ == "__main__":
    ingest_pdf()
