"""Orquestra os agentes em pipelines e os agenda via APScheduler.

O Core (este módulo) só conhece a interface `Agent` — os agentes concretos e os
plugins que eles usam são montados em `main.py` (composition root) e injetados aqui.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from opportunity_squad.core.interfaces.agent import Agent, AgentContext, AgentResult
from opportunity_squad.core.interfaces.report_generator import ReportPeriod
from opportunity_squad.core.logging import get_logger
from opportunity_squad.db.models.enums import RunStatus
from opportunity_squad.db.models.ops import Run
from opportunity_squad.db.session import session_scope

logger = get_logger("scheduler")


class SquadOrchestrator:
    """Executa pipelines de agentes em sequência, registrando cada execução em `runs`."""

    def __init__(self, agents: dict[str, Agent]) -> None:
        self._agents = agents

    def run_pipeline(self, agent_names: list[str], *, trigger: str, data: dict | None = None) -> list[AgentResult]:
        run_id = str(uuid.uuid4())
        context = AgentContext(run_id=run_id, data=dict(data or {}))
        results: list[AgentResult] = []

        with session_scope() as session:
            run_row = Run(started_at=datetime.now(UTC), status=RunStatus.RUNNING, trigger=trigger)
            session.add(run_row)
            session.flush()
            run_row_id = run_row.id

        for agent_name in agent_names:
            agent = self._agents.get(agent_name)
            if agent is None:
                logger.warning("agent_not_registered", agent_name=agent_name)
                continue
            result = agent.run(context)
            results.append(result)
            if not result.success:
                logger.error("pipeline_step_failed", agent=agent_name, error=result.error)

        context.data["run_results"] = results
        if "memory" in self._agents:
            self._agents["memory"].run(context)

        overall_status = RunStatus.SUCCESS if all(r.success for r in results) else RunStatus.PARTIAL
        with session_scope() as session:
            run_row = session.get(Run, run_row_id)
            run_row.finished_at = datetime.now(UTC)
            run_row.status = overall_status
            run_row.summary = {r.agent_name: r.success for r in results}

        return results

    def run_scan_pipeline(self) -> list[AgentResult]:
        """Pipeline principal: descoberta -> qualificação -> análise -> estratégia."""
        return self.run_pipeline(
            [
                "scout",
                "discovery",
                "review",
                "sentiment",
                "trend",
                "competitor",
                "market",
                "gap",
                "strategy",
                "security",
            ],
            trigger="scheduler:scan",
        )

    def run_report_pipeline(self, period: ReportPeriod) -> list[AgentResult]:
        """Pipeline de relatório: gera o relatório do período e notifica."""
        report_results = self.run_pipeline(
            ["report"], trigger=f"scheduler:report:{period.value}", data={"period": period.value}
        )
        report_output: dict = next(
            (r.output for r in report_results if r.agent_name == "report"), {}
        )
        report_id = report_output.get("report_id")
        return self.run_pipeline(
            ["notification"],
            trigger=f"scheduler:notify:{period.value}",
            data={"report_id": report_id},
        )

    def run_mvp_pipeline(self) -> list[AgentResult]:
        """Pipeline de execução: transforma ideias validadas em MVPs com roadmap técnico."""
        return self.run_pipeline(["mvp", "architecture"], trigger="scheduler:mvp")


def build_scheduler(orchestrator: SquadOrchestrator, settings) -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone=settings.timezone)

    scheduler.add_job(
        orchestrator.run_scan_pipeline,
        trigger=IntervalTrigger(minutes=settings.scan_interval_minutes),
        id="scan_pipeline",
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        lambda: orchestrator.run_report_pipeline(ReportPeriod.DAILY),
        trigger=CronTrigger(hour=settings.daily_report_hour, minute=0),
        id="daily_report",
        max_instances=1,
    )
    scheduler.add_job(
        lambda: orchestrator.run_report_pipeline(ReportPeriod.WEEKLY),
        trigger=CronTrigger(day_of_week=settings.weekly_report_day, hour=settings.daily_report_hour),
        id="weekly_report",
        max_instances=1,
    )
    scheduler.add_job(
        lambda: orchestrator.run_report_pipeline(ReportPeriod.MONTHLY),
        trigger=CronTrigger(day=settings.monthly_report_day, hour=settings.daily_report_hour),
        id="monthly_report",
        max_instances=1,
    )
    scheduler.add_job(
        orchestrator.run_mvp_pipeline,
        trigger=IntervalTrigger(hours=6),
        id="mvp_pipeline",
        max_instances=1,
        coalesce=True,
    )

    return scheduler
