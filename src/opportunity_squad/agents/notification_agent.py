"""Notification Agent: entrega alertas pendentes e relatórios via o canal de notificação configurado."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from opportunity_squad.core.interfaces.agent import Agent, AgentContext
from opportunity_squad.core.interfaces.notifier import NotificationLevel, Notifier
from opportunity_squad.db.models.report import Alert, Report
from opportunity_squad.db.session import session_scope

_LEVEL_MAP = {
    "info": NotificationLevel.INFO,
    "opportunity": NotificationLevel.OPPORTUNITY,
    "report": NotificationLevel.REPORT,
    "error": NotificationLevel.ERROR,
}


class NotificationAgent(Agent):
    name = "notification"

    def __init__(self, notifier: Notifier):
        super().__init__()
        self._notifier = notifier

    def execute(self, context: AgentContext) -> dict[str, Any]:
        delivered = 0
        with session_scope() as session:
            alerts = session.query(Alert).filter_by(delivered=False).limit(50).all()
            for alert in alerts:
                level = _LEVEL_MAP.get(alert.level.value, NotificationLevel.INFO)
                self._notifier.send(alert.message, level=level)
                alert.delivered = True
                alert.delivered_at = datetime.now(UTC)
                delivered += 1

            report_id = context.data.get("report_id")
            if report_id:
                report = session.get(Report, report_id)
                if report and report.sent_at is None:
                    self._notifier.send(report.content, level=NotificationLevel.REPORT)
                    report.sent_at = datetime.now(UTC)

        return {"delivered": delivered}
