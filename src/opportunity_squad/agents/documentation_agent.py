"""Documentation Agent: regenera docs/architecture/plugins.md a partir do plugin registry."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from opportunity_squad.core.interfaces.agent import Agent, AgentContext

if TYPE_CHECKING:
    from plugins.registry import PluginManifest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_OUTPUT_FILE = _REPO_ROOT / "docs" / "architecture" / "plugins.md"


class DocumentationAgent(Agent):
    name = "documentation"

    def execute(self, context: AgentContext) -> dict[str, Any]:
        from plugins.registry import (
            discover_all,  # import tardio: plugins/ não é um pacote instalado
        )

        manifests = discover_all()
        content = self._render(manifests)
        _OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        _OUTPUT_FILE.write_text(content, encoding="utf-8")

        total = sum(len(items) for items in manifests.values())
        return {"plugins": total}

    @staticmethod
    def _render(manifests: dict[str, dict[str, PluginManifest]]) -> str:
        lines = [
            "# Plugins instalados",
            "",
            "_Gerado automaticamente pelo Documentation Agent._",
            "",
        ]
        for category, plugins in manifests.items():
            lines.append(f"## {category}")
            if not plugins:
                lines.append("_Nenhum plugin implementado ainda._")
            for name, manifest in plugins.items():
                lines.append(f"- **{name}** — {manifest.description.strip()}")
            lines.append("")
        return "\n".join(lines)
