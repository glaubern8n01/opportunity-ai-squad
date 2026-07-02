"""Análise de mercado (Market Agent) e de tendências (Trend Agent)."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from opportunity_squad.db.base import Base, TimestampMixin
from opportunity_squad.db.models.enums import TrendDirection


class MarketAnalysis(Base, TimestampMixin):
    __tablename__ = "market_analysis"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    market_size: Mapped[str | None] = mapped_column(String(255), nullable=True)
    growth_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    geography: Mapped[str | None] = mapped_column(String(50), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_by: Mapped[str] = mapped_column(String(80), default="market_agent")


class TrendAnalysis(Base, TimestampMixin):
    __tablename__ = "trend_analysis"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    direction: Mapped[TrendDirection] = mapped_column(default=TrendDirection.STABLE)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    window: Mapped[str] = mapped_column(String(20), default="7d")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
