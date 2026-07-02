"""Reviews/avaliações normalizadas de produtos, com sentimento preenchido pelo Sentiment Agent."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from opportunity_squad.db.base import Base, TimestampMixin
from opportunity_squad.db.models.enums import SentimentLabel


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)

    source: Mapped[str] = mapped_column(String(80))
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_rating: Mapped[float] = mapped_column(Float, default=5.0)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentiment: Mapped[SentimentLabel | None] = mapped_column(nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
