"""Fontes de dados cadastradas e log de execução de cada fetch por fonte."""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from opportunity_squad.db.base import Base, TimestampMixin
from opportunity_squad.db.models.enums import SourceLogStatus


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50))
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(default=True)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class SourcesLog(Base, TimestampMixin):
    __tablename__ = "sources_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    run_id: Mapped[int | None] = mapped_column(
        ForeignKey("runs.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[SourceLogStatus] = mapped_column(default=SourceLogStatus.SUCCESS)
    items_fetched: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
