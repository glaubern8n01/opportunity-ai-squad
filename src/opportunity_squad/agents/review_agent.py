"""Review Agent: busca reviews para produtos qualificados que ainda não têm avaliações salvas."""

from __future__ import annotations

from opportunity_squad.core.interfaces.agent import Agent, AgentContext, AgentResult
from opportunity_squad.core.interfaces.source import SourceConnector
from opportunity_squad.db.models.product import Product
from opportunity_squad.db.models.review import Review
from opportunity_squad.db.models.source import Source
from opportunity_squad.db.session import session_scope


class ReviewAgent(Agent):
    name = "review"

    def __init__(self, sources: dict[str, SourceConnector], *, min_score: float = 3.0):
        super().__init__()
        self._sources = sources
        self._min_score = min_score

    def run(self, context: AgentContext) -> AgentResult:
        try:
            fetched = 0
            with session_scope() as session:
                for source_name, connector in self._sources.items():
                    source_row = session.query(Source).filter_by(name=source_name).one_or_none()
                    if source_row is None:
                        continue

                    candidates = (
                        session.query(Product)
                        .filter(Product.source_id == source_row.id)
                        .filter(Product.opportunity_score >= self._min_score)
                        .all()
                    )
                    for product in candidates:
                        already_has_reviews = (
                            session.query(Review.id).filter_by(product_id=product.id).first()
                        )
                        if already_has_reviews:
                            continue
                        for review in connector.fetch_reviews(product.external_id):
                            session.add(
                                Review(
                                    product_id=product.id,
                                    source=review.source,
                                    author=review.author,
                                    rating=review.rating,
                                    max_rating=review.max_rating,
                                    title=review.title,
                                    body=review.body,
                                    published_at=review.published_at,
                                    url=review.url,
                                )
                            )
                            fetched += 1

            self.logger.info("review_completed", fetched=fetched)
            return AgentResult(agent_name=self.name, success=True, output={"fetched": fetched})
        except Exception as exc:
            self.logger.error("review_failed", error=str(exc))
            return AgentResult(agent_name=self.name, success=False, error=str(exc))
