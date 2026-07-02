"""Sentiment Agent: classifica o sentimento de reviews ainda não rotuladas, via IA."""

from __future__ import annotations

from typing import Any

from opportunity_squad.core.interfaces.agent import Agent, AgentContext
from opportunity_squad.core.interfaces.ai_provider import AIProvider, ModelTier
from opportunity_squad.db.models.enums import SentimentLabel
from opportunity_squad.db.models.review import Review
from opportunity_squad.db.session import session_scope

_SYSTEM_PROMPT = (
    "Você classifica o sentimento de reviews de produtos digitais. "
    "Responda apenas com uma palavra: positive, neutral ou negative."
)


class SentimentAgent(Agent):
    name = "sentiment"

    def __init__(self, ai_provider: AIProvider, *, batch_size: int = 50):
        super().__init__()
        self._ai = ai_provider
        self._batch_size = batch_size

    def execute(self, context: AgentContext) -> dict[str, Any]:
        classified = 0
        with session_scope() as session:
            reviews = (
                session.query(Review)
                .filter(Review.sentiment.is_(None))
                .filter(Review.body.isnot(None))
                .limit(self._batch_size)
                .all()
            )
            for review in reviews:
                label = self._classify(review.body)
                if label:
                    review.sentiment = label
                    classified += 1

        return {"classified": classified}

    def _classify(self, body: str) -> SentimentLabel | None:
        response = self._ai.complete(
            body[:2000],
            system=_SYSTEM_PROMPT,
            tier=ModelTier.CHEAP,
            max_tokens=5,
            temperature=0.0,
        )
        normalized = response.strip().lower()
        for label in SentimentLabel:
            if label.value in normalized:
                return label
        return None
