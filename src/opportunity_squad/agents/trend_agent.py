"""Trend Agent: compara os dois últimos snapshots de métricas para detectar tendência."""

from __future__ import annotations

from opportunity_squad.core.interfaces.agent import Agent, AgentContext, AgentResult
from opportunity_squad.db.models.enums import ProductStatus, TrendDirection
from opportunity_squad.db.models.market import TrendAnalysis
from opportunity_squad.db.models.product import Product, ProductVersion
from opportunity_squad.db.session import session_scope

_STATUS_FOR_DIRECTION = {
    TrendDirection.UP: ProductStatus.PROMISING,
    TrendDirection.DOWN: ProductStatus.DECLINING,
    TrendDirection.STABLE: ProductStatus.ACTIVE,
}


class TrendAgent(Agent):
    name = "trend"

    def run(self, context: AgentContext) -> AgentResult:
        try:
            analyzed = 0
            with session_scope() as session:
                for product in session.query(Product).all():
                    versions = (
                        session.query(ProductVersion)
                        .filter_by(product_id=product.id)
                        .order_by(ProductVersion.captured_at.desc())
                        .limit(2)
                        .all()
                    )
                    if len(versions) < 2:
                        continue

                    latest, previous = versions
                    direction, score = self._compare(latest, previous)
                    product.status = _STATUS_FOR_DIRECTION[direction]

                    session.add(
                        TrendAnalysis(
                            keyword=product.name,
                            direction=direction,
                            score=score,
                            window="latest_vs_previous",
                        )
                    )
                    analyzed += 1

            self.logger.info("trend_completed", analyzed=analyzed)
            return AgentResult(agent_name=self.name, success=True, output={"analyzed": analyzed})
        except Exception as exc:
            self.logger.error("trend_failed", error=str(exc))
            return AgentResult(agent_name=self.name, success=False, error=str(exc))

    @staticmethod
    def _compare(
        latest: ProductVersion, previous: ProductVersion
    ) -> tuple[TrendDirection, float]:
        latest_signal = latest.upvotes or 0
        previous_signal = previous.upvotes or 0
        if previous_signal == 0:
            return (TrendDirection.STABLE, 0.0)

        change_ratio = (latest_signal - previous_signal) / previous_signal
        if change_ratio > 0.1:
            return (TrendDirection.UP, round(change_ratio * 10, 2))
        if change_ratio < -0.1:
            return (TrendDirection.DOWN, round(change_ratio * 10, 2))
        return (TrendDirection.STABLE, round(change_ratio * 10, 2))
