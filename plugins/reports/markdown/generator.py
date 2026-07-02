"""Plugin de relatório: renderiza o resumo periódico (diário/semanal/mensal) em Markdown."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from opportunity_squad.core.interfaces.report_generator import ReportGenerator, ReportPeriod

_PERIOD_LABEL = {
    ReportPeriod.DAILY: "Resumo Diário",
    ReportPeriod.WEEKLY: "Resumo Semanal",
    ReportPeriod.MONTHLY: "Resumo Mensal",
}

_SECTIONS: list[tuple[str, str]] = [
    ("top_products", "🏆 Top Produtos"),
    ("top_startups", "🚀 Top Startups"),
    ("top_opportunities", "💡 Top Oportunidades"),
    ("top_complaints", "😠 Top Reclamações"),
    ("top_features", "✨ Top Funcionalidades Pedidas"),
    ("growing_markets", "📈 Mercados em Crescimento"),
    ("declining_products", "📉 Produtos em Queda"),
    ("promising_products", "🌱 Produtos Promissores"),
]


class MarkdownReportGenerator(ReportGenerator):
    name = "markdown"
    file_extension = "md"

    def generate(self, period: ReportPeriod, data: dict[str, Any]) -> str:
        generated_at = data.get("generated_at", datetime.now(UTC))
        lines = [
            f"# {_PERIOD_LABEL.get(period, str(period))} — Opportunity AI Squad",
            "",
            f"_Gerado em {generated_at:%Y-%m-%d %H:%M UTC}_",
            "",
        ]

        for key, title in _SECTIONS:
            items = data.get(key) or []
            lines.append(f"## {title}")
            if not items:
                lines.append("_Nada relevante neste período._")
            else:
                for item in items:
                    lines.append(self._render_item(item))
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _render_item(item: Any) -> str:
        if isinstance(item, dict):
            name = item.get("name", "?")
            score = item.get("score")
            url = item.get("url")
            score_part = f" — score `{score}`" if score is not None else ""
            url_part = f" — [link]({url})" if url else ""
            return f"- **{name}**{score_part}{url_part}"
        return f"- {item}"
