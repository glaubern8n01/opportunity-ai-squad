"""Plugin de fonte: extração estruturada de páginas públicas via API hospedada da
ScrapeGraphAI (SDK oficial `scrapegraph-py`).

Diferente de `github_trending`/`hacker_news` (que consomem uma API oficial já
estruturada de uma fonte fixa), este conector é genérico: usa `search()` para
combinar uma busca na web com extração via LLM (server-side, na ScrapeGraphAI) e
`extract()` para detalhar uma página específica a partir do `external_id` (que aqui
é a própria URL do item, não um id nativo de uma fonte). Serve para cobrir fontes
sem API oficial, sem fazer scraping direto/agressivo — a renderização e o respeito a
robots.txt são responsabilidade do serviço da ScrapeGraphAI.
"""

from __future__ import annotations

import hashlib
from typing import Any

from scrapegraph_py import ScrapeGraphAI

from opportunity_squad.core.entities.product import NormalizedProduct, ReviewData
from opportunity_squad.core.exceptions import SourceFetchError
from opportunity_squad.core.interfaces.source import SourceConnector

_DEFAULT_QUERY = "novos produtos SaaS e ferramentas de IA lançados recentemente"

_EXTRACTION_PROMPT = (
    "Extraia produtos, SaaS, apps ou ferramentas de IA mencionados nesta página. "
    "Ignore navegação, anúncios e conteúdo não relacionado a produtos."
)

_LIST_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "tagline": {"type": "string"},
                    "description": {"type": "string"},
                    "url": {"type": "string"},
                    "pricing_model": {"type": "string"},
                    "has_free_plan": {"type": "boolean"},
                    "category": {"type": "string"},
                },
                "required": ["name"],
            },
        }
    },
    "required": ["products"],
}

_REVIEWS_PROMPT = (
    "Extraia depoimentos, avaliações ou reviews de usuários mencionados nesta página, "
    "com autor (se houver) e o texto do depoimento."
)

_REVIEWS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "reviews": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "author": {"type": "string"},
                    "body": {"type": "string"},
                    "rating": {"type": "number"},
                },
                "required": ["body"],
            },
        }
    },
    "required": ["reviews"],
}


class ScrapeGraphAIConnector(SourceConnector):
    name = "scrapegraph_ai"

    def initialize(self, config: dict[str, Any]) -> None:
        self._client = ScrapeGraphAI(api_key=config["api_key"])
        self._default_query = config.get("default_query") or _DEFAULT_QUERY
        self._num_results = int(config.get("num_results") or 5)

    def shutdown(self) -> None:
        super().shutdown()
        self._client.close()

    @SourceConnector.with_retry()
    def search(self, query: str | None = None, **kwargs: Any) -> list[NormalizedProduct]:
        effective_query = query or self._default_query
        cache_key = f"search:{effective_query}"
        cached = self.cache_get(cache_key)
        if cached is not None:
            return cached

        result = self._client.search(
            effective_query,
            num_results=kwargs.get("num_results", self._num_results),
            prompt=_EXTRACTION_PROMPT,
            schema=_LIST_SCHEMA,
        )
        if result.status != "success" or result.data is None:
            raise SourceFetchError(f"ScrapeGraphAI search falhou: {result.error}")

        items = (result.data.json_data or {}).get("products", [])
        products = [self.normalize(item) for item in items]
        self.logs("search_completed", query=effective_query, results=len(products))
        self.cache_set(cache_key, products)
        return products

    @SourceConnector.with_retry()
    def fetch_details(self, external_id: str) -> NormalizedProduct:
        if not external_id.startswith(("http://", "https://")):
            raise SourceFetchError(
                f"fetch_details requer uma URL como external_id, recebido: '{external_id}'"
            )

        result = self._client.extract(
            _EXTRACTION_PROMPT,
            url=external_id,
            schema=_LIST_SCHEMA,
        )
        if result.status != "success" or result.data is None:
            raise SourceFetchError(f"ScrapeGraphAI extract falhou: {result.error}")

        items = (result.data.json_data or {}).get("products", [])
        if not items:
            raise SourceFetchError(f"Nenhum produto extraído de '{external_id}'")
        item = dict(items[0])
        item.setdefault("url", external_id)
        return self.normalize(item)

    def fetch_reviews(self, external_id: str) -> list[ReviewData]:
        """Melhor esforço: tenta extrair depoimentos/reviews da própria página do produto.

        Retorna lista vazia (em vez de propagar erro) se a URL não suportar extração de
        reviews — nem toda página de produto tem essa seção, e isso não deve interromper
        o pipeline de Scout/Discovery.
        """
        if not external_id.startswith(("http://", "https://")):
            return []
        try:
            result = self._client.extract(
                _REVIEWS_PROMPT,
                url=external_id,
                schema=_REVIEWS_SCHEMA,
            )
        except Exception:
            return []
        if result.status != "success" or result.data is None:
            return []

        raw_reviews = (result.data.json_data or {}).get("reviews", [])
        return [
            ReviewData(
                source=self.name,
                author=raw.get("author"),
                rating=raw.get("rating"),
                body=raw.get("body"),
                url=external_id,
                raw=raw,
            )
            for raw in raw_reviews
            if raw.get("body")
        ]

    def normalize(self, raw: dict[str, Any]) -> NormalizedProduct:
        url = raw.get("url")
        external_id = url or _synthetic_id(raw.get("name", ""))
        return NormalizedProduct(
            source=self.name,
            external_id=external_id,
            name=raw.get("name") or external_id,
            tagline=raw.get("tagline"),
            description=raw.get("description"),
            url=url,
            website=url,
            category=raw.get("category"),
            pricing_model=raw.get("pricing_model"),
            has_free_plan=raw.get("has_free_plan"),
            raw=raw,
        )


def _synthetic_id(name: str) -> str:
    """Fallback determinístico quando o item extraído não tem URL própria.

    Sem URL não há como reconsultar via fetch_details, mas ainda precisamos de um
    external_id estável para a constraint uq_products_source_external.
    """
    return "sha256:" + hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]
