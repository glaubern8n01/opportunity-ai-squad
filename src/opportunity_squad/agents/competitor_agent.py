"""Competitor Agent: usa IA para levantar concorrentes prováveis de um produto."""

from __future__ import annotations

import json

from opportunity_squad.core.interfaces.agent import Agent, AgentContext, AgentResult
from opportunity_squad.core.interfaces.ai_provider import AIProvider, ModelTier
from opportunity_squad.db.models.competitor import Competitor
from opportunity_squad.db.models.product import Product
from opportunity_squad.db.session import session_scope

_SYSTEM_PROMPT = (
    "Você é um analista de mercado. Dado um produto digital, liste até 5 concorrentes diretos "
    'conhecidos. Responda APENAS com JSON: [{"name": "...", "url": "..."}, ...]. '
    "Se não souber, responda []."
)


class CompetitorAgent(Agent):
    name = "competitor"

    def __init__(self, ai_provider: AIProvider, *, batch_size: int = 20):
        super().__init__()
        self._ai = ai_provider
        self._batch_size = batch_size

    def run(self, context: AgentContext) -> AgentResult:
        try:
            mapped = 0
            with session_scope() as session:
                products = (
                    session.query(Product)
                    .outerjoin(Competitor, Competitor.product_id == Product.id)
                    .filter(Competitor.id.is_(None))
                    .filter(Product.opportunity_score.isnot(None))
                    .limit(self._batch_size)
                    .all()
                )
                for product in products:
                    for competitor in self._find_competitors(product):
                        session.add(
                            Competitor(
                                product_id=product.id,
                                name=competitor.get("name", "?"),
                                url=competitor.get("url"),
                            )
                        )
                        mapped += 1

            self.logger.info("competitor_completed", mapped=mapped)
            return AgentResult(agent_name=self.name, success=True, output={"mapped": mapped})
        except Exception as exc:
            self.logger.error("competitor_failed", error=str(exc))
            return AgentResult(agent_name=self.name, success=False, error=str(exc))

    def _find_competitors(self, product: Product) -> list[dict]:
        prompt = (
            f"Produto: {product.name}\nDescrição: {product.description or product.tagline or ''}"
        )
        response = self._ai.complete(
            prompt,
            system=_SYSTEM_PROMPT,
            tier=ModelTier.STANDARD,
            max_tokens=500,
            temperature=0.2,
        )
        try:
            data = json.loads(response)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            self.logger.warning("competitor_parse_failed", product_id=product.id)
            return []
