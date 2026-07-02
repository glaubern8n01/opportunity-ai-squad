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
    """Unidade de responsabilidade única do squad (Scout, Discovery, Review, ...).

    `run()` é um template method: centraliza o try/except e o log de sucesso/falha
    para que nenhum agente concreto precise repetir esse boilerplate (nem possa
    esquecer de capturar uma exceção). Agentes concretos implementam `execute()`,
    que pode lançar livremente — qualquer exceção vira `AgentResult(success=False)`.
    """

    name: str = "unnamed_agent"

    def __init__(self) -> None:
        self.logger = structlog.get_logger(f"agent.{self.name}")

    def run(self, context: AgentContext) -> AgentResult:
        try:
            output = self.execute(context) or {}
        except Exception as exc:  # noqa: BLE001 - fronteira do agente: nunca propaga
            self.logger.error(f"{self.name}_failed", error=str(exc))
            return AgentResult(agent_name=self.name, success=False, error=str(exc))

        self.logger.info(f"{self.name}_completed", **output)
        return AgentResult(agent_name=self.name, success=True, output=output)

    @abstractmethod
    def execute(self, context: AgentContext) -> dict[str, Any]:
        """Implementa a lógica do agente. Pode lançar — `run()` converte em `AgentResult`."""
