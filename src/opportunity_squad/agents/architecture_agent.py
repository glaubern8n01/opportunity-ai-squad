"""Architecture Agent: gera um roadmap técnico (milestones) para MVPs em planejamento."""

from __future__ import annotations

import json
from typing import Any

from opportunity_squad.core.interfaces.agent import Agent, AgentContext
from opportunity_squad.core.interfaces.ai_provider import AIProvider, ModelTier
from opportunity_squad.db.models.enums import MvpStatus
from opportunity_squad.db.models.ideation import MvpProject, Roadmap
from opportunity_squad.db.session import session_scope

_SYSTEM_PROMPT = (
    "Você é um arquiteto de software sênior. Dado um MVP e sua stack, proponha um roadmap de "
    'execução. Responda APENAS com JSON: {"milestones": [{"title": "...", "description": "..."}]} '
    "(4 a 8 marcos, do setup inicial ao lançamento)."
)


class ArchitectureAgent(Agent):
    name = "architecture"

    def __init__(self, ai_provider: AIProvider, *, batch_size: int = 10):
        super().__init__()
        self._ai = ai_provider
        self._batch_size = batch_size

    def execute(self, context: AgentContext) -> dict[str, Any]:
        created = 0
        with session_scope() as session:
            projects = (
                session.query(MvpProject)
                .outerjoin(Roadmap, Roadmap.mvp_project_id == MvpProject.id)
                .filter(Roadmap.id.is_(None))
                .filter(MvpProject.status == MvpStatus.PLANNING)
                .limit(self._batch_size)
                .all()
            )
            for project in projects:
                milestones = self._plan_milestones(project)
                if not milestones:
                    continue
                session.add(
                    Roadmap(
                        mvp_project_id=project.id,
                        title=f"Roadmap — {project.name}",
                        milestones=milestones,
                    )
                )
                created += 1

        return {"created": created}

    def _plan_milestones(self, project: MvpProject) -> list[dict] | None:
        prompt = f"MVP: {project.name}\nStack: {project.stack or 'a definir'}"
        response = self._ai.complete(
            prompt, system=_SYSTEM_PROMPT, tier=ModelTier.DEEP, max_tokens=800, temperature=0.3
        )
        try:
            data = json.loads(response)
            return data.get("milestones")
        except json.JSONDecodeError:
            self.logger.warning("architecture_parse_failed", project_id=project.id)
            return None
