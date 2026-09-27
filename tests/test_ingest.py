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
