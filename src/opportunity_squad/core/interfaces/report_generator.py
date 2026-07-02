"""Contrato para plugins de geração de relatório (plugins/reports/<nome>)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any


class ReportPeriod(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReportGenerator(ABC):
    """Plugin de formato de relatório (markdown, html, pdf, ...)."""

    name: str = "unnamed_report_format"
    file_extension: str = "txt"

    def initialize(self, config: dict[str, Any]) -> None:
        """A maioria dos formatos é sem estado; override apenas se precisar de config."""

    @abstractmethod
    def generate(self, period: ReportPeriod, data: dict[str, Any]) -> str:
        """Recebe os dados agregados do período e retorna o relatório renderizado."""
