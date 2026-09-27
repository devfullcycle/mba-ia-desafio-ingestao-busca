import pytest

from ingest import ingest_pdf


def test_ingest_pdf_exits_when_pdf_missing(tmp_path, monkeypatch, capsys):
    missing_pdf = tmp_path / "does-not-exist.pdf"

    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    )
    monkeypatch.setenv("PG_VECTOR_COLLECTION_NAME", "test_collection")
    monkeypatch.setenv("PDF_PATH", str(missing_pdf))

    with pytest.raises(SystemExit) as exc_info:
        ingest_pdf()

    assert exc_info.value.code == 1
    assert "não encontrado" in capsys.readouterr().out


def test_ingest_pdf_exits_when_required_config_missing(tmp_path, monkeypatch, capsys):
    # Roda a partir de um diretório sem .env, senão get_settings() carregaria o .env
    # real do repositório e mascararia o cenário de configuração ausente.
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PG_VECTOR_COLLECTION_NAME", raising=False)
    monkeypatch.delenv("PDF_PATH", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        ingest_pdf()

    assert exc_info.value.code == 1
    assert "configuração" in capsys.readouterr().out.lower()
