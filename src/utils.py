from langchain_core.documents import Document


def validate_chunks(chunks: list[Document]) -> None:
    """Valida se a lista de chunks não está vazia.

    Args:
        chunks: Lista de documentos (chunks) a serem validados.

    Raises:
        ValueError: Se a lista de chunks estiver vazia.
    """
    if not chunks:
        raise ValueError("A lista de chunks não pode estar vazia. Verifique o arquivo PDF.")