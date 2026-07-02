"""Strategy Agent: usa IA para estimar os 13 critérios do Opportunity Score e persiste a análise."""

from __future__ import annotations

import json
from typing import Any

from opportunity_squad.core.interfaces.agent import Agent, AgentContext
from opportunity_squad.core.interfaces.ai_provider import AIProvider, ModelTier
from opportunity_squad.db.models.analysis import Analysis
from opportunity_squad.db.models.product import Product
from opportunity_squad.db.session import session_scope
from opportunity_squad.scoring.opportunity_score import calculate_opportunity_score

_CRITERIA_KEYS = (
    "market",
    "competition",
    "estimated_revenue",
    "reviews",
    "users_and_downloads",
    "trend",
    "dev_ease",
    "ai_potential",
    "automation_potential",
    "scalability",
    "complexity_penalty",
    "monetization_chance",
    "virality_chance",
)

_SYSTEM_PROMPT = (
    "Você avalia oportunidades de produtos digitais. Dado um produto, estime cada critério "
    "abaixo em uma escala 0-10, onde 10 é sempre 'melhor oportunidade' (inclusive para "
    "'competition', onde 10 = pouca concorrência, e 'complexity_penalty', onde 10 = baixa "
    f"complexidade). Responda APENAS com JSON contendo as chaves: {list(_CRITERIA_KEYS)}."
)


class StrategyAgent(Agent):
    name = "strategy"

    def __init__(self, ai_provider: AIProvider, *, batch_size: int = 20):
        super().__init__()
        self._ai = ai_provider
        self._batch_size = batch_size

    def execute(self, context: AgentContext) -> dict[str, Any]:
        scored = 0
        with session_scope() as session:
            products = (
                session.query(Product)
                .outerjoin(Analysis, Analysis.product_id == Product.id)
                .filter(Analysis.id.is_(None))
                .filter(Product.opportunity_score.isnot(None))
                .limit(self._batch_size)
                .all()
            )
            for product in products:
                criteria = self._estimate_criteria(product)
                if criteria is None:
                    continue
                result = calculate_opportunity_score(criteria)
                session.add(
                    Analysis(
                        product_id=product.id,
                        agent_name=self.name,
                        final_score=result.final_score,
                        score_breakdown=result.model_dump(),
                        summary=result.notes,
                    )
                )
                product.opportunity_score = result.final_score
                scored += 1

        return {"scored": scored}

    def _estimate_criteria(self, product: Product) -> dict[str, float] | None:
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
            return {key: float(data[key]) for key in _CRITERIA_KEYS}
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            self.logger.warning("strategy_parse_failed", product_id=product.id)
            return None
