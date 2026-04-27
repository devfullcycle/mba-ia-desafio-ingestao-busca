try:
    from config import ConfigurationError, load_settings, validate_provider_credentials
except ImportError:  # pragma: no cover - fallback for package imports
    from src.config import ConfigurationError, load_settings, validate_provider_credentials

def ingest_pdf():
    settings = load_settings()
    validate_provider_credentials(settings)
    return settings


if __name__ == "__main__":
    try:
        ingest_pdf()
    except ConfigurationError as exc:
        print(exc)
        raise SystemExit(1) from exc
