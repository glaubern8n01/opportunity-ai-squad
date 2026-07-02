"""Contrato para plugins de notificação (plugins/notifications/<nome>)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any


class NotificationLevel(StrEnum):
    INFO = "info"
    OPPORTUNITY = "opportunity"
    REPORT = "report"
    ERROR = "error"


class Notifier(ABC):
    """Plugin de canal de notificação. O Core dispara eventos sem saber o canal concreto."""

    name: str = "unnamed_notifier"

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> None:
        """Configura credenciais/cliente a partir do dict de config do plugin."""

    @abstractmethod
    def send(self, message: str, *, level: NotificationLevel = NotificationLevel.INFO) -> None:
        """Envia uma mensagem de texto simples pelo canal."""

    def send_document(self, path: str, *, caption: str | None = None) -> None:
        """Envia um arquivo (ex: relatório em PDF/Markdown). Override opcional."""
        raise NotImplementedError(f"{self.name} não suporta envio de documentos")

    def shutdown(self) -> None:
        """Override opcional para liberar recursos."""
