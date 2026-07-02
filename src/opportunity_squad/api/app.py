"""FastAPI opcional — expõe healthcheck e o catálogo de plugins. Não é o entrypoint principal
(esse é `opportunity_squad.main`, que roda o scheduler); a API serve para observabilidade/futuro
dashboard (ver ROADMAP.md)."""

from __future__ import annotations

from fastapi import FastAPI

from opportunity_squad.core.config import get_settings

app = FastAPI(title="Opportunity AI Squad", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app_env": settings.app_env}


@app.get("/plugins")
def list_plugins() -> dict[str, list[str]]:
    from plugins.registry import discover_all

    return {category: sorted(manifests) for category, manifests in discover_all().items()}
