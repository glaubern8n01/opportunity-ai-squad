"""MVP Agent: transforma ideias validadas em um plano de MVP (stack + features) via IA."""

from __future__ import annotations

import json
from typing import Any

from opportunity_squad.core.interfaces.agent import Agent, AgentContext
from opportunity_squad.core.interfaces.ai_provider import AIProvider, ModelTier
from opportunity_squad.db.models.enums import IdeaStatus, MvpStatus
from opportunity_squad.db.models.ideation import Feature, Idea, MvpProject
from opportunity_squad.db.session import session_scope

_SYSTEM_PROMPT = (
    "Você é um arquiteto de produto. Dada uma ideia validada, proponha um MVP enxuto. Responda "
    'APENAS com JSON: {"name": "...", "stack": "...", "features": ["...", "..."]} '
    "(3 a 6 features)."
)


class MvpAgent(Agent):
    name = "mvp"

    def __init__(self, ai_provider: AIProvider, *, min_score: float = 7.0, batch_size: int = 10):
        super().__init__()
        self._ai = ai_provider
        self._min_score = min_score
        self._batch_size = batch_size

    def execute(self, context: AgentContext) -> dict[str, Any]:
        created = 0
        with session_scope() as session:
            ideas = (
                session.query(Idea)
                .filter(Idea.status == IdeaStatus.VALIDATED)
                .filter(Idea.opportunity_score >= self._min_score)
                .limit(self._batch_size)
                .all()
            )
            for idea in ideas:
                plan = self._draft_plan(idea)
                if not plan or not plan.get("name"):
                    continue
                mvp = MvpProject(
                    idea_id=idea.id,
                    name=plan["name"],
                    stack=plan.get("stack"),
                    status=MvpStatus.PLANNING,
                )
                session.add(mvp)
                session.flush()
                for feature_name in plan.get("features", []):
                    session.add(Feature(mvp_project_id=mvp.id, name=feature_name))
                idea.status = IdeaStatus.IN_PROGRESS
                created += 1

        return {"created": created}

    def _draft_plan(self, idea: Idea) -> dict | None:
        prompt = f"Ideia: {idea.title}\nDescrição: {idea.description or ''}"
        response = self._ai.complete(
            prompt, system=_SYSTEM_PROMPT, tier=ModelTier.DEEP, max_tokens=600, temperature=0.4
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            self.logger.warning("mvp_parse_failed", idea_id=idea.id)
            return None
