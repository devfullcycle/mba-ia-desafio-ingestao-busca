from __future__ import annotations

from typing import Callable

try:
    from config import ConfigurationError, load_settings, validate_provider_credentials
    from search import SearchServiceError, answer_question
except ImportError:  # pragma: no cover - fallback for package imports
    from src.config import ConfigurationError, load_settings, validate_provider_credentials
    from src.search import SearchServiceError, answer_question


def _print_debug_chunks(result: dict, print_func: Callable[[str], None]) -> None:
    documents = result.get("documents", [])
    if not documents:
        print_func("DEBUG CHUNKS: nenhum trecho recuperado.")
        return

    print_func("DEBUG CHUNKS:")
    for index, chunk in enumerate(documents, start=1):
        metadata = getattr(chunk, "metadata", {}) or {}
        page = metadata.get("page", "n/a")
        source = metadata.get("source", "n/a")
        score = getattr(chunk, "score", "n/a")
        content = getattr(chunk, "content", "").strip()
        print_func(
            f"- trecho={index} score={score} page={page} source={source} texto={content}"
        )


def main(
    *,
    input_func: Callable[[str], str] = input,
    print_func: Callable[[str], None] = print,
) -> int:
    settings = load_settings()
    validate_provider_credentials(settings)

    while True:
        try:
            question = input_func("PERGUNTA: ").strip()
        except KeyboardInterrupt:
            print_func("\nEncerrando chat.")
            return 0
        except EOFError:
            print_func("\nEncerrando chat.")
            return 0

        if not question:
            print_func("Encerrando chat.")
            return 0

        try:
            result = answer_question(question)
        except (ConfigurationError, SearchServiceError) as exc:
            print_func(f"Nao foi possivel responder a pergunta. {exc}")
            return 1

        print_func(f"RESPOSTA: {result['answer']}")

        if settings.debug_retrieved_chunks:
            _print_debug_chunks(result, print_func)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigurationError as exc:
        print(exc)
        raise SystemExit(1) from exc
