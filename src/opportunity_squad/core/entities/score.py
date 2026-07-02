"""Resultado do cálculo de Opportunity Score (0-10)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OpportunityScoreResult(BaseModel):
    """Nota final e o detalhamento por critério, para rastreabilidade no relatório."""

    final_score: float = Field(ge=0, le=10)
    market: float = Field(ge=0, le=10)
    competition: float = Field(ge=0, le=10)
    estimated_revenue: float = Field(ge=0, le=10)
    reviews: float = Field(ge=0, le=10)
    users_and_downloads: float = Field(ge=0, le=10)
    trend: float = Field(ge=0, le=10)
    dev_ease: float = Field(ge=0, le=10)
    ai_potential: float = Field(ge=0, le=10)
    automation_potential: float = Field(ge=0, le=10)
    scalability: float = Field(ge=0, le=10)
    complexity_penalty: float = Field(ge=0, le=10)
    monetization_chance: float = Field(ge=0, le=10)
    virality_chance: float = Field(ge=0, le=10)
    notes: str | None = None
