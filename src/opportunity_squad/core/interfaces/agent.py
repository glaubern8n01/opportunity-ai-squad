"""Contrato base para todos os agentes (src/opportunity_squad/agents/<nome>_agent.py).

Diferente dos plugins de infraestrutura (source/ai/notifier/report), os agentes fazem
parte do domínio da aplicação e orquestram plugins através das interfaces acima —
nunca importam um plugin concreto diretamente.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import structlog


@dataclass
class AgentContext:
    """Estado compartilhado passado entre agentes durante uma execução (run)."""

    run_id: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    agent_name: str
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Agent(ABC):
    """Unidade de responsabilidade única do squad (Scout, Discovery, Review, ...)."""

    name: str = "unnamed_agent"

    def __init__(self) -> None:
        self.logger = structlog.get_logger(f"agent.{self.name}")

    @abstractmethod
    def run(self, context: AgentContext) -> AgentResult:
        """Executa a responsabilidade do agente e retorna o resultado, sem lançar exceção."""
