"""Watchlist e favoritos. `owner` identifica quem marcou (ex: chat id do Telegram);
o sistema é single-tenant por padrão ("default") até que autenticação seja adicionada."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from opportunity_squad.db.base import Base, TimestampMixin


class Watchlist(Base, TimestampMixin):
    __tablename__ = "watchlist"
    __table_args__ = (UniqueConstraint("product_id", "owner", name="uq_watchlist_product_owner"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    owner: Mapped[str] = mapped_column(String(120), default="default")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Favorite(Base, TimestampMixin):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("product_id", "owner", name="uq_favorites_product_owner"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    owner: Mapped[str] = mapped_column(String(120), default="default")
