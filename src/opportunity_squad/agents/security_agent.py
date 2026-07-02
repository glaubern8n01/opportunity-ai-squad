"""Security Agent: valida configuração obrigatória e faz uma varredura leve por segredos óbvios.

Não substitui o Gitleaks do CI (ver .github/workflows/gitleaks.yml) — é uma checagem
em tempo de execução, útil para alertar caso algo escape para o ambiente de runtime.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from opportunity_squad.core.config import Settings, get_settings
from opportunity_squad.core.interfaces.agent import Agent, AgentContext
from opportunity_squad.db.models.enums import AlertLevel
from opportunity_squad.db.models.report import Alert
from opportunity_squad.db.session import session_scope

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]
_SCAN_GLOBS = ("*.py", "*.yaml", "*.yml", "*.toml", "*.json")
_SKIP_DIRS = {".git", ".venv", "node_modules", ".agents", "__pycache__"}


class SecurityAgent(Agent):
    name = "security"

    def execute(self, context: AgentContext) -> dict[str, Any]:
        issues = self._check_required_config() + self._scan_for_secrets()
        if issues:
            with session_scope() as session:
                session.add(
                    Alert(
                        level=AlertLevel.ERROR,
                        message="Security Agent encontrou problemas:\n" + "\n".join(issues),
                    )
                )
        return {"issues_count": len(issues), "issues": issues}

    @staticmethod
    def _check_required_config() -> list[str]:
        settings: Settings = get_settings()
        issues = []
        if settings.ai_provider == "anthropic" and not settings.anthropic_api_key:
            issues.append("ANTHROPIC_API_KEY ausente com AI_PROVIDER=anthropic")
        if "telegram" in settings.enabled_notification_plugins and (
            not settings.telegram_bot_token or not settings.telegram_chat_id
        ):
            issues.append("TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID ausentes com telegram habilitado")
        return issues

    @classmethod
    def _scan_for_secrets(cls) -> list[str]:
        issues = []
        for glob in _SCAN_GLOBS:
            for path in _REPO_ROOT.rglob(glob):
                if any(part in _SKIP_DIRS for part in path.parts):
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for pattern in _SECRET_PATTERNS:
                    if pattern.search(text):
                        issues.append(f"possível segredo em {path.relative_to(_REPO_ROOT)}")
        return issues
