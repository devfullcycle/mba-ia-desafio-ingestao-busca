from langchain_core.documents import Document
from pathlib import Path
import os


def validate_chunks(value:list[Document]):
    if not value:
        raise SystemError(0)
    pass

# Extrair para Utils, criar testes e documentar
def resolve_path() -> Path:
    PDF_PATH = os.getenv("PDF_PATH")
    user_path = Path(PDF_PATH)
    if(not user_path.is_absolute()):
        user_path = user_path.resolve()
    
    if not user_path.exists():
        raise FileExistsError(f"Arquivo não encontrado: {user_path}")

    return user_path

class AdditionalMetadata():
    def __init__(self, embedding_type):
        self.embedding_type = embedding_type