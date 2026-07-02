"""Relatórios gerados (diário/semanal/mensal) e alertas disparados para notificação."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from opportunity_squad.db.base import Base, TimestampMixin
from opportunity_squad.db.models.enums import AlertLevel, ReportPeriodEnum


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[ReportPeriodEnum] = mapped_column(index=True)
    format: Mapped[str] = mapped_column(String(20), default="markdown")
    content: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[AlertLevel] = mapped_column(default=AlertLevel.INFO, index=True)
    message: Mapped[str] = mapped_column(Text)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=True
    )
    delivered: Mapped[bool] = mapped_column(default=False, index=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
