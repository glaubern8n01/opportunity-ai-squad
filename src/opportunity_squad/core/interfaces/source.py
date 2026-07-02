"""Contrato que todo plugin de fonte de dados (plugins/sources/<nome>) deve implementar.

O Core nunca importa uma fonte concreta — apenas depende desta interface (DIP).
Retry, cache e logging são resolvidos aqui como comportamento comum (mixin),
para que cada plugin só precise implementar a lógica específica da fonte.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from opportunity_squad.core.entities.product import NormalizedProduct, ReviewData


class SourceConnector(ABC):
    """Plugin de fonte de dados. Uma instância por fonte (ex: product_hunt, reddit, github)."""

    #: identificador único usado em ENABLED_SOURCE_PLUGINS e no campo `source` das entidades
    name: str = "unnamed_source"

    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, Any]] = {}
        self._cache_ttl_seconds = 900
        self.logger = structlog.get_logger(f"source.{self.name}")

    # -- ciclo de vida ----------------------------------------------------
    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> None:
        """Configura credenciais/clientes HTTP a partir do dict de config do plugin."""

    def shutdown(self) -> None:
        """Libera recursos (conexões HTTP, etc). Override opcional."""
        self._cache.clear()

    # -- contrato principal -------------------------------------------------
    @abstractmethod
    def search(self, query: str | None = None, **kwargs: Any) -> list[NormalizedProduct]:
        """Busca produtos/lançamentos na fonte. `query=None` significa 'últimos/trending'."""

    @abstractmethod
    def fetch_details(self, external_id: str) -> NormalizedProduct:
        """Busca detalhes completos de um único item pelo id nativo da fonte."""

    @abstractmethod
    def fetch_reviews(self, external_id: str) -> list[ReviewData]:
        """Busca reviews/avaliações de um item. Retorna lista vazia se a fonte não suportar."""

    @abstractmethod
    def normalize(self, raw: dict[str, Any]) -> NormalizedProduct:
        """Converte o payload cru da API/feed da fonte em NormalizedProduct."""

    def validate(self, product: NormalizedProduct) -> bool:
        """Validação mínima antes de persistir. Override para regras específicas da fonte."""
        return bool(product.external_id and product.name)

    def score(self, product: NormalizedProduct) -> float:
        """Pré-score heurístico e barato (0-10), usado para priorizar antes da análise por IA."""
        signal = 0.0
        if product.upvotes:
            signal += min(product.upvotes / 100, 4.0)
        if product.users_count:
            signal += min(product.users_count / 10_000, 3.0)
        if product.reviews:
            signal += min(len(product.reviews) / 20, 3.0)
        return round(min(signal, 10.0), 2)

    # -- cross-cutting: retry -------------------------------------------------
    @staticmethod
    def with_retry(max_attempts: int = 3):
        """Decorator de retry com backoff exponencial para chamadas de rede dos plugins."""
        return retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        )

    # -- cross-cutting: cache -------------------------------------------------
    def cache_get(self, key: str) -> Any | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._cache[key]
            return None
        return value

    def cache_set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self._cache_ttl_seconds
        self._cache[key] = (time.monotonic() + ttl, value)

    # -- cross-cutting: logs -------------------------------------------------
    def logs(self, event: str, **kwargs: Any) -> None:
        self.logger.info(event, source=self.name, **kwargs)
