"""Plugin de fonte: repositórios em alta no GitHub via Search API oficial.

Usa https://api.github.com/search/repositories (API pública e documentada) em vez de
fazer scraping da página /trending, que não é uma API oficial e muda sem aviso.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from opportunity_squad.core.entities.product import NormalizedProduct, ReviewData
from opportunity_squad.core.exceptions import SourceFetchError
from opportunity_squad.core.interfaces.source import SourceConnector

_API_BASE = "https://api.github.com"


class GitHubTrendingConnector(SourceConnector):
    name = "github_trending"

    def initialize(self, config: dict[str, Any]) -> None:
        headers = {"Accept": "application/vnd.github+json"}
        token = config.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(base_url=_API_BASE, headers=headers, timeout=15.0)

    def shutdown(self) -> None:
        super().shutdown()
        self._client.close()

    @SourceConnector.with_retry()
    def search(self, query: str | None = None, **kwargs: Any) -> list[NormalizedProduct]:
        cache_key = f"search:{query}:{kwargs.get('language', '')}"
        cached = self.cache_get(cache_key)
        if cached is not None:
            return cached

        since = (datetime.now(UTC) - timedelta(days=7)).strftime("%Y-%m-%d")
        q = query or f"created:>{since} stars:>10"
        if language := kwargs.get("language"):
            q += f" language:{language}"

        response = self._client.get(
            "/search/repositories",
            params={"q": q, "sort": "stars", "order": "desc", "per_page": kwargs.get("limit", 25)},
        )
        if response.status_code != 200:
            raise SourceFetchError(f"GitHub search falhou ({response.status_code}): {response.text}")

        items = response.json().get("items", [])
        products = [self.normalize(item) for item in items]
        self.logs("search_completed", query=q, results=len(products))
        self.cache_set(cache_key, products)
        return products

    @SourceConnector.with_retry()
    def fetch_details(self, external_id: str) -> NormalizedProduct:
        response = self._client.get(f"/repos/{external_id}")
        if response.status_code != 200:
            raise SourceFetchError(
                f"GitHub repo '{external_id}' falhou ({response.status_code}): {response.text}"
            )
        return self.normalize(response.json())

    def fetch_reviews(self, external_id: str) -> list[ReviewData]:
        # GitHub não tem conceito de "review" público de produto; sem dados aqui.
        return []

    def normalize(self, raw: dict[str, Any]) -> NormalizedProduct:
        return NormalizedProduct(
            source=self.name,
            external_id=raw["full_name"],
            name=raw["name"],
            tagline=raw.get("description"),
            description=raw.get("description"),
            url=raw.get("html_url"),
            category=raw.get("language"),
            tags=raw.get("topics", []),
            upvotes=raw.get("stargazers_count"),
            website=raw.get("homepage") or raw.get("html_url"),
            launched_at=_parse_dt(raw.get("created_at")),
            raw=raw,
        )


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
