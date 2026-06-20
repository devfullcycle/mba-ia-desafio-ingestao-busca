import os
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai

# Carrega variáveis do .env (raiz do projeto)
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY não encontrada. Verifique o arquivo .env")

genai.configure(api_key=api_key)

models = genai.list_models()

output_path = Path(__file__).parent / "modelos.txt"

with open(output_path, "w", encoding="utf-8") as f:
    for model in models:
        f.write(f"{model.name}\n")
        f.write(f"Supported Actions: {model.supported_generation_methods}\n")
        f.write("-" * 20 + "\n")

print(f"Lista de modelos salva em: {output_path}")
