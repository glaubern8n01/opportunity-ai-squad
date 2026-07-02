"""Gap Agent: cruza reviews negativas para identificar lacunas de funcionalidades (ideias)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import func

from opportunity_squad.core.interfaces.agent import Agent, AgentContext
from opportunity_squad.core.interfaces.ai_provider import AIProvider, ModelTier
from opportunity_squad.db.models.enums import IdeaStatus, SentimentLabel
from opportunity_squad.db.models.ideation import Idea
from opportunity_squad.db.models.product import Product
from opportunity_squad.db.models.review import Review
from opportunity_squad.db.session import session_scope

_SYSTEM_PROMPT = (
    "Você identifica lacunas de produto a partir de reclamações de usuários. Responda APENAS "
    'com JSON: {"title": "...", "description": "..."} descrevendo a oportunidade de melhoria '
    "mais recorrente, ou {} se não houver reclamações suficientes."
)


class GapAgent(Agent):
    name = "gap"

    def __init__(self, ai_provider: AIProvider, *, min_negative_reviews: int = 3):
        super().__init__()
        self._ai = ai_provider
        self._min_negative_reviews = min_negative_reviews

    def execute(self, context: AgentContext) -> dict[str, Any]:
        created = 0
        with session_scope() as session:
            products = (
                session.query(Product)
                .join(Review, Review.product_id == Product.id)
                .filter(Review.sentiment == SentimentLabel.NEGATIVE)
                .group_by(Product.id)
                .having(func.count(Review.id) >= self._min_negative_reviews)
                .all()
            )
            for product in products:
                negative_bodies = [
                    review.body
                    for review in session.query(Review)
                    .filter_by(product_id=product.id, sentiment=SentimentLabel.NEGATIVE)
                    .limit(10)
                    .all()
                    if review.body
                ]
                idea = self._extract_gap(product, negative_bodies)
                if not idea or not idea.get("title"):
                    continue
                session.add(
                    Idea(
                        title=idea["title"],
                        description=idea.get("description"),
                        based_on_product_id=product.id,
                        status=IdeaStatus.NEW,
                    )
                )
                created += 1

        return {"created": created}

    def _extract_gap(self, product: Product, complaints: list[str]) -> dict | None:
        prompt = f"Produto: {product.name}\nReclamações:\n" + "\n---\n".join(complaints)
        response = self._ai.complete(
            prompt,
            system=_SYSTEM_PROMPT,
            tier=ModelTier.STANDARD,
            max_tokens=300,
            temperature=0.3,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            self.logger.warning("gap_parse_failed", product_id=product.id)
            return None
