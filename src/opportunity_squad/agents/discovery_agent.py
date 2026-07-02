"""Discovery Agent: aplica um pré-score heurístico (sem IA) e sinaliza candidatos p/ análise."""

from __future__ import annotations

from typing import Any

from opportunity_squad.core.interfaces.agent import Agent, AgentContext
from opportunity_squad.db.models.product import Product, ProductVersion
from opportunity_squad.db.session import session_scope


class DiscoveryAgent(Agent):
    name = "discovery"

    def __init__(self, *, min_score: float = 3.0):
        super().__init__()
        self._min_score = min_score

    def execute(self, context: AgentContext) -> dict[str, Any]:
        qualified = 0
        with session_scope() as session:
            products = session.query(Product).filter_by(opportunity_score=None).all()
            for product in products:
                latest_version = (
                    session.query(ProductVersion)
                    .filter_by(product_id=product.id)
                    .order_by(ProductVersion.captured_at.desc())
                    .first()
                )
                pre_score = self._heuristic_score(latest_version)
                product.opportunity_score = pre_score
                if pre_score >= self._min_score:
                    qualified += 1

        return {"qualified": qualified}

    @staticmethod
    def _heuristic_score(version: ProductVersion | None) -> float:
        if version is None:
            return 0.0
        signal = 0.0
        if version.upvotes:
            signal += min(version.upvotes / 100, 4.0)
        if version.users_count:
            signal += min(version.users_count / 10_000, 3.0)
        if version.reviews_count:
            signal += min(version.reviews_count / 20, 3.0)
        return round(min(signal, 10.0), 2)
