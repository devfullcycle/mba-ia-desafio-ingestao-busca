try:
    from config import ConfigurationError, load_settings, validate_provider_credentials
    from search import search_prompt
except ImportError:  # pragma: no cover - fallback for package imports
    from src.config import ConfigurationError, load_settings, validate_provider_credentials
    from src.search import search_prompt

def main():
    settings = load_settings()
    validate_provider_credentials(settings)

    prompt = search_prompt()
    if not prompt:
        print("Nao foi possivel iniciar o chat. Verifique os erros de inicializacao.")
        return 1

    print("Chat pronto para a SI-01.2+.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigurationError as exc:
        print(exc)
        raise SystemExit(1) from exc
