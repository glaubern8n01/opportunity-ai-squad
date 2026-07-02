"""Contrato para plugins de provedor de IA (plugins/ai/<nome>)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any


class ModelTier(StrEnum):
    """Nível de custo/capacidade solicitado pelo agente que está chamando a IA."""

    CHEAP = "cheap"  # ex: Haiku — processamento em massa, barato
    STANDARD = "standard"  # ex: Sonnet — análises completas
    DEEP = "deep"  # ex: Opus — análises profundas, poucas chamadas


class AIProvider(ABC):
    """Plugin de provedor de IA. O Core só conhece esta interface, nunca o SDK concreto."""

    name: str = "unnamed_provider"

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> None:
        """Configura API key/cliente a partir do dict de config do plugin."""

    @abstractmethod
    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        tier: ModelTier = ModelTier.STANDARD,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> str:
        """Executa uma chamada de completions/mensagens e retorna o texto de resposta."""

    def shutdown(self) -> None:
        """Override opcional para liberar recursos."""
