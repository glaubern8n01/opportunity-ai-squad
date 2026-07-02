"""Market Agent: usa IA para estimar tamanho/crescimento de mercado e resumir o cenário."""

from __future__ import annotations

import json

from opportunity_squad.core.interfaces.agent import Agent, AgentContext, AgentResult
from opportunity_squad.core.interfaces.ai_provider import AIProvider, ModelTier
from opportunity_squad.db.models.market import MarketAnalysis
from opportunity_squad.db.models.product import Product
from opportunity_squad.db.session import session_scope

_SYSTEM_PROMPT = (
    "Você é um analista de mercado. Dado um produto digital, responda APENAS com JSON: "
    '{"market_size": "...", "growth_rate": <float ou null>, '
    '"geography": "br|international|global", "summary": "..."}'
)


class MarketAgent(Agent):
    name = "market"

    def __init__(self, ai_provider: AIProvider, *, batch_size: int = 20):
        super().__init__()
        self._ai = ai_provider
        self._batch_size = batch_size

    def run(self, context: AgentContext) -> AgentResult:
        try:
            analyzed = 0
            with session_scope() as session:
                products = (
                    session.query(Product)
                    .outerjoin(MarketAnalysis, MarketAnalysis.product_id == Product.id)
                    .filter(MarketAnalysis.id.is_(None))
                    .filter(Product.opportunity_score.isnot(None))
                    .limit(self._batch_size)
                    .all()
                )
                for product in products:
                    data = self._analyze(product)
                    if data is None:
                        continue
                    session.add(
                        MarketAnalysis(
                            product_id=product.id,
                            market_size=data.get("market_size"),
                            growth_rate=data.get("growth_rate"),
                            geography=data.get("geography"),
                            summary=data.get("summary"),
                            generated_by=self.name,
                        )
                    )
                    analyzed += 1

            self.logger.info("market_completed", analyzed=analyzed)
            return AgentResult(agent_name=self.name, success=True, output={"analyzed": analyzed})
        except Exception as exc:
            self.logger.error("market_failed", error=str(exc))
            return AgentResult(agent_name=self.name, success=False, error=str(exc))

    def _analyze(self, product: Product) -> dict | None:
        prompt = (
            f"Produto: {product.name}\nDescrição: {product.description or product.tagline or ''}"
        )
        response = self._ai.complete(
            prompt,
            system=_SYSTEM_PROMPT,
            tier=ModelTier.STANDARD,
            max_tokens=400,
            temperature=0.2,
        )
        try:
            data = json.loads(response)
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            self.logger.warning("market_parse_failed", product_id=product.id)
            return None
