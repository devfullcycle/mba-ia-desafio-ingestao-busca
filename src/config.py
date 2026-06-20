import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de Banco e Coleção
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "document_embeddings")

# Configuração de PDF
PDF_PATH = os.getenv("PDF_PATH", "document.pdf")

# Configuração de Modelos IA
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL", "models/gemini-3.1-flash-lite-preview")

# Configuração de Rate Limit
RATE_LIMIT_TPM = 30_000
CHARS_PER_TOKEN = 2
SAFETY_MARGIN = 0.75
