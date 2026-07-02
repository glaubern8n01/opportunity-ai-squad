"""Memory Agent: registra o resultado de cada run e mantém o MEMORY.md sincronizado."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from opportunity_squad.core.interfaces.agent import Agent, AgentContext, AgentResult

_REPO_ROOT = Path(__file__).resolve().parents[3]
_MEMORY_FILE = _REPO_ROOT / "MEMORY.md"


class MemoryAgent(Agent):
    name = "memory"

    def run(self, context: AgentContext) -> AgentResult:
        try:
            results: list[AgentResult] = context.data.get("run_results", [])
            entry = self._render_entry(context.run_id, results)
            self._append(entry)
            self.logger.info("memory_completed", run_id=context.run_id)
            return AgentResult(agent_name=self.name, success=True, output={"run_id": context.run_id})
        except Exception as exc:
            self.logger.error("memory_failed", error=str(exc))
            return AgentResult(agent_name=self.name, success=False, error=str(exc))

    @staticmethod
    def _render_entry(run_id: str, results: list[AgentResult]) -> str:
        lines = [f"\n## Run `{run_id}` — {datetime.now(UTC):%Y-%m-%d %H:%M UTC}\n"]
        for result in results:
            status = "OK" if result.success else f"FALHOU: {result.error}"
            lines.append(f"- **{result.agent_name}**: {status} — {result.output}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _append(entry: str) -> None:
        if not _MEMORY_FILE.exists():
            _MEMORY_FILE.write_text("# MEMORY\n", encoding="utf-8")
        with _MEMORY_FILE.open("a", encoding="utf-8") as handle:
            handle.write(entry)
