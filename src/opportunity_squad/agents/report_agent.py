"""Report Agent: agrega dados do período e gera o relatório via plugin de report (ex: markdown)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from opportunity_squad.core.interfaces.agent import Agent, AgentContext
from opportunity_squad.core.interfaces.report_generator import ReportGenerator, ReportPeriod
from opportunity_squad.db.models.enums import ProductStatus, ReportPeriodEnum
from opportunity_squad.db.models.product import Product
from opportunity_squad.db.models.report import Report
from opportunity_squad.db.session import session_scope

_WINDOW_DAYS = {ReportPeriod.DAILY: 1, ReportPeriod.WEEKLY: 7, ReportPeriod.MONTHLY: 30}


class ReportAgent(Agent):
    name = "report"

    def __init__(self, report_generator: ReportGenerator):
        super().__init__()
        self._generator = report_generator

    def execute(self, context: AgentContext) -> dict[str, Any]:
        period = ReportPeriod(context.data.get("period", ReportPeriod.DAILY.value))
        with session_scope() as session:
            since = datetime.now(UTC) - timedelta(days=_WINDOW_DAYS[period])
            top_products = (
                session.query(Product)
                .filter(Product.first_seen_at >= since)
                .filter(Product.opportunity_score.isnot(None))
                .order_by(Product.opportunity_score.desc())
                .limit(10)
                .all()
            )
            promising = (
                session.query(Product)
                .filter(Product.status == ProductStatus.PROMISING)
                .order_by(Product.opportunity_score.desc().nulls_last())
                .limit(10)
                .all()
            )
            declining = (
                session.query(Product)
                .filter(Product.status == ProductStatus.DECLINING)
                .limit(10)
                .all()
            )

            data = {
                "generated_at": datetime.now(UTC),
                "top_products": [_to_item(p) for p in top_products],
                "promising_products": [_to_item(p) for p in promising],
                "declining_products": [_to_item(p) for p in declining],
            }
            content = self._generator.generate(period, data)

            report_row = Report(
                period=ReportPeriodEnum(period.value),
                format=self._generator.file_extension,
                content=content,
            )
            session.add(report_row)
            session.flush()
            report_id = report_row.id

        return {"period": period.value, "report_id": report_id}


def _to_item(product: Product) -> dict:
    return {"name": product.name, "score": product.opportunity_score, "url": product.url}
