from __future__ import annotations

from pathlib import Path

import yaml


def test_docker_compose_keeps_required_services_and_bootstrap() -> None:
    compose = yaml.safe_load(Path("docker-compose.yml").read_text(encoding="utf-8"))

    services = compose["services"]
    assert {"postgres", "bootstrap_vector_ext", "app"} <= set(services)
    assert services["postgres"]["image"] == "pgvector/pgvector:pg17"
    assert services["bootstrap_vector_ext"]["depends_on"]["postgres"]["condition"] == "service_healthy"
    assert "CREATE EXTENSION IF NOT EXISTS vector;" in services["bootstrap_vector_ext"]["command"]


def test_app_service_uses_devcontainer_image_and_shared_workspace_mount() -> None:
    compose = yaml.safe_load(Path("docker-compose.yml").read_text(encoding="utf-8"))

    app = compose["services"]["app"]
    assert app["build"]["dockerfile"] == "Dockerfile.dev"
    assert ".:/app" in app["volumes"]
    assert app["depends_on"]["bootstrap_vector_ext"]["condition"] == "service_completed_successfully"
