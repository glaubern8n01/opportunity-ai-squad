"""Scout Agent: varre as fontes habilitadas e persiste produtos novos/atualizados."""

from __future__ import annotations

from opportunity_squad.core.entities.product import NormalizedProduct
from opportunity_squad.core.interfaces.agent import Agent, AgentContext, AgentResult
from opportunity_squad.core.interfaces.source import SourceConnector
from opportunity_squad.db.models.product import Product, ProductVersion
from opportunity_squad.db.models.source import Source
from opportunity_squad.db.session import session_scope


class ScoutAgent(Agent):
    name = "scout"

    def __init__(self, sources: dict[str, SourceConnector]):
        super().__init__()
        self._sources = sources

    def run(self, context: AgentContext) -> AgentResult:
        try:
            discovered = 0
            with session_scope() as session:
                for source_name, connector in self._sources.items():
                    source_row = session.query(Source).filter_by(name=source_name).one_or_none()
                    if source_row is None:
                        source_row = Source(name=source_name, category="sources", is_enabled=True)
                        session.add(source_row)
                        session.flush()

                    for product in connector.search(**context.data.get(source_name, {})):
                        if not connector.validate(product):
                            continue
                        self._upsert(session, source_row.id, product)
                        discovered += 1

            self.logger.info("scout_completed", discovered=discovered)
            return AgentResult(
                agent_name=self.name, success=True, output={"discovered": discovered}
            )
        except Exception as exc:
            self.logger.error("scout_failed", error=str(exc))
            return AgentResult(agent_name=self.name, success=False, error=str(exc))

    @staticmethod
    def _upsert(session, source_id: int, product: NormalizedProduct) -> Product:
        row = (
            session.query(Product)
            .filter_by(source_id=source_id, external_id=product.external_id)
            .one_or_none()
        )
        if row is None:
            row = Product(source_id=source_id, external_id=product.external_id, name=product.name)
            session.add(row)

        row.name = product.name
        row.tagline = product.tagline
        row.description = product.description
        row.url = product.url
        row.website = product.website
        row.logo_url = product.logo_url
        row.pricing_model = product.pricing_model
        row.has_free_plan = product.has_free_plan
        row.launched_at = product.launched_at
        session.flush()

        session.add(
            ProductVersion(
                product_id=row.id,
                upvotes=product.upvotes,
                downloads=product.downloads,
                users_count=product.users_count,
                reviews_count=len(product.reviews),
                raw=product.raw,
            )
        )
        return row
