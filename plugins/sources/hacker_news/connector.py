"""Plugin de fonte: Hacker News via API oficial pública (Firebase), sem autenticação."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from opportunity_squad.core.entities.product import NormalizedProduct, ReviewData
from opportunity_squad.core.exceptions import SourceFetchError
from opportunity_squad.core.interfaces.source import SourceConnector

_API_BASE = "https://hacker-news.firebaseio.com/v0"


class HackerNewsConnector(SourceConnector):
    name = "hacker_news"

    def initialize(self, config: dict[str, Any]) -> None:
        self._client = httpx.Client(base_url=_API_BASE, timeout=15.0)

    def shutdown(self) -> None:
        super().shutdown()
        self._client.close()

    @SourceConnector.with_retry()
    def search(self, query: str | None = None, **kwargs: Any) -> list[NormalizedProduct]:
        """`query` é ignorado — a API do HN não tem busca; usamos showstories (Show HN)."""
        cache_key = f"search:showhn:{kwargs.get('limit', 20)}"
        cached = self.cache_get(cache_key)
        if cached is not None:
            return cached

        limit = kwargs.get("limit", 20)
        ids = self._get_json("/showstories.json")[:limit]
        products = [self.fetch_details(str(item_id)) for item_id in ids]
        self.logs("search_completed", results=len(products))
        self.cache_set(cache_key, products)
        return products

    @SourceConnector.with_retry()
    def fetch_details(self, external_id: str) -> NormalizedProduct:
        raw = self._get_json(f"/item/{external_id}.json")
        if raw is None:
            raise SourceFetchError(f"Item HN '{external_id}' não encontrado")
        return self.normalize(raw)

    def fetch_reviews(self, external_id: str) -> list[ReviewData]:
        """Trata os primeiros comentários do post como 'reviews' informais da comunidade."""
        raw = self._get_json(f"/item/{external_id}.json") or {}
        comment_ids = (raw.get("kids") or [])[:10]
        reviews: list[ReviewData] = []
        for comment_id in comment_ids:
            comment = self._get_json(f"/item/{comment_id}.json")
            if not comment or comment.get("deleted") or comment.get("dead"):
                continue
            reviews.append(
                ReviewData(
                    source=self.name,
                    author=comment.get("by"),
                    body=comment.get("text"),
                    published_at=_from_unix(comment.get("time")),
                    url=f"https://news.ycombinator.com/item?id={comment_id}",
                    raw=comment,
                )
            )
        return reviews

    def normalize(self, raw: dict[str, Any]) -> NormalizedProduct:
        item_id = str(raw["id"])
        return NormalizedProduct(
            source=self.name,
            external_id=item_id,
            name=raw.get("title", f"HN #{item_id}"),
            tagline=raw.get("title"),
            url=raw.get("url") or f"https://news.ycombinator.com/item?id={item_id}",
            upvotes=raw.get("score"),
            website=raw.get("url"),
            launched_at=_from_unix(raw.get("time")),
            raw=raw,
        )

    def _get_json(self, path: str) -> Any:
        response = self._client.get(path)
        if response.status_code != 200:
            raise SourceFetchError(f"HN request '{path}' falhou ({response.status_code})")
        return response.json()


def _from_unix(value: int | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromtimestamp(value, UTC)
