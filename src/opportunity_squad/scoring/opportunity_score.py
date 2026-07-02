"""Cálculo do Opportunity Score (0-10) a partir dos critérios definidos no briefing.

Cada critério de entrada já deve estar normalizado em uma escala 0-10 onde **10 é
sempre "melhor oportunidade"** — inclusive `competition` (10 = pouca concorrência)
e `complexity_penalty` (10 = baixa complexidade). Essa normalização é responsabilidade
de quem produz os critérios (tipicamente o Strategy Agent, com apoio de IA).
"""

from __future__ import annotations

from opportunity_squad.core.entities.score import OpportunityScoreResult

# Pesos somam 1.0 — ajustáveis conforme o squad aprender o que realmente prediz sucesso.
_WEIGHTS: dict[str, float] = {
    "market": 0.10,
    "competition": 0.08,
    "estimated_revenue": 0.12,
    "reviews": 0.06,
    "users_and_downloads": 0.08,
    "trend": 0.08,
    "dev_ease": 0.06,
    "ai_potential": 0.10,
    "automation_potential": 0.08,
    "scalability": 0.08,
    "complexity_penalty": 0.06,
    "monetization_chance": 0.06,
    "virality_chance": 0.04,
}


def calculate_opportunity_score(
    criteria: dict[str, float], *, notes: str | None = None
) -> OpportunityScoreResult:
    """Recebe os 13 critérios (0-10 cada) e retorna a nota final ponderada + o detalhamento."""
    missing = _WEIGHTS.keys() - criteria.keys()
    if missing:
        raise ValueError(f"Critérios ausentes para o Opportunity Score: {sorted(missing)}")

    final_score = sum(criteria[key] * weight for key, weight in _WEIGHTS.items())

    return OpportunityScoreResult(
        final_score=round(final_score, 2),
        notes=notes,
        **{key: criteria[key] for key in _WEIGHTS},
    )
