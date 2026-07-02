"""Produtos/oportunidades rastreados e o histórico de métricas ao longo do tempo."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from opportunity_squad.db.base import Base, TimestampMixin
from opportunity_squad.db.models.enums import ProductStatus
from opportunity_squad.db.models.taxonomy import Tag, product_tags


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("source_id", "external_id", name="uq_products_source_external"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    external_id: Mapped[str] = mapped_column(String(255), index=True)

    name: Mapped[str] = mapped_column(String(255), index=True)
    tagline: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    website: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    pricing_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    has_free_plan: Mapped[bool | None] = mapped_column(nullable=True)

    launched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    opportunity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[ProductStatus] = mapped_column(default=ProductStatus.ACTIVE, index=True)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tags: Mapped[list[Tag]] = relationship(secondary=product_tags)


class ProductVersion(Base):
    """Snapshot periódico de métricas de um produto — base para o Trend Agent."""

    __tablename__ = "product_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    upvotes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    downloads: Mapped[int | None] = mapped_column(Integer, nullable=True)
    users_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating_avg: Mapped[float | None] = mapped_column(Float, nullable=True)
    reviews_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
