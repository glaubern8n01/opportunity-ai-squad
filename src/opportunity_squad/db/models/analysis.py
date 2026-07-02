"""Análise completa de um produto: qualitativa (Review/Strategy Agents) + Opportunity Score."""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from opportunity_squad.db.base import Base, TimestampMixin


class Analysis(Base, TimestampMixin):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    agent_name: Mapped[str] = mapped_column(String(80))

    strengths: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    ux_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    performance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    copy_difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    technical_complexity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    market_br_potential: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_intl_potential: Mapped[float | None] = mapped_column(Float, nullable=True)
    saas_potential: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Opportunity Score (0-10) — ver core.entities.score.OpportunityScoreResult
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    score_breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
