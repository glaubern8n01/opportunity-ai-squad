"""Discovery Agent: aplica um pré-score heurístico (sem IA) e sinaliza candidatos p/ análise."""

from __future__ import annotations

from opportunity_squad.core.interfaces.agent import Agent, AgentContext, AgentResult
from opportunity_squad.db.models.product import Product, ProductVersion
from opportunity_squad.db.session import session_scope


class DiscoveryAgent(Agent):
    name = "discovery"

    def __init__(self, *, min_score: float = 3.0):
        super().__init__()
        self._min_score = min_score

    def run(self, context: AgentContext) -> AgentResult:
        try:
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

            self.logger.info("discovery_completed", qualified=qualified)
            return AgentResult(
                agent_name=self.name, success=True, output={"qualified": qualified}
            )
        except Exception as exc:
            self.logger.error("discovery_failed", error=str(exc))
            return AgentResult(agent_name=self.name, success=False, error=str(exc))

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
