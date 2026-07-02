"""Plugin de notificação: Telegram."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import telegram
from telegram.constants import ParseMode

from opportunity_squad.core.exceptions import ConfigurationError, NotificationError
from opportunity_squad.core.interfaces.notifier import NotificationLevel, Notifier

_LEVEL_PREFIX = {
    NotificationLevel.INFO: "ℹ️",
    NotificationLevel.OPPORTUNITY: "🚀",
    NotificationLevel.REPORT: "📊",
    NotificationLevel.ERROR: "🔴",
}


class TelegramNotifier(Notifier):
    name = "telegram"

    def initialize(self, config: dict[str, Any]) -> None:
        bot_token = config.get("bot_token")
        chat_id = config.get("chat_id")
        if not bot_token or not chat_id:
            raise ConfigurationError("TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID são obrigatórios")

        self._chat_id = chat_id
        self._bot = telegram.Bot(token=bot_token)

    def send(self, message: str, *, level: NotificationLevel = NotificationLevel.INFO) -> None:
        prefix = _LEVEL_PREFIX.get(level, "")
        text = f"{prefix} {message}".strip()
        try:
            asyncio.run(
                self._bot.send_message(
                    chat_id=self._chat_id, text=text, parse_mode=ParseMode.MARKDOWN
                )
            )
        except telegram.error.TelegramError as exc:
            raise NotificationError(f"Falha ao enviar mensagem no Telegram: {exc}") from exc

    def send_document(self, path: str, *, caption: str | None = None) -> None:
        file_path = Path(path)
        try:
            with file_path.open("rb") as handle:
                asyncio.run(
                    self._bot.send_document(
                        chat_id=self._chat_id, document=handle, caption=caption
                    )
                )
        except telegram.error.TelegramError as exc:
            raise NotificationError(f"Falha ao enviar documento no Telegram: {exc}") from exc
