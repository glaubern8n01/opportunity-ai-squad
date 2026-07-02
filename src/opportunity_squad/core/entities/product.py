"""Entidades de domínio para produtos/oportunidades normalizados. Independentes do ORM."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ReviewData(BaseModel):
    """Uma avaliação/review normalizada, independente da fonte original."""

    source: str
    author: str | None = None
    rating: float | None = None
    max_rating: float = 5.0
    title: str | None = None
    body: str | None = None
    published_at: datetime | None = None
    url: str | None = None
    raw: dict = Field(default_factory=dict)


class NormalizedProduct(BaseModel):
    """Formato comum que todo SourceConnector deve produzir a partir de search()/fetch_details()."""

    source: str
    external_id: str
    name: str
    tagline: str | None = None
    description: str | None = None
    url: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    pricing_model: str | None = None
    has_free_plan: bool | None = None
    upvotes: int | None = None
    downloads: int | None = None
    users_count: int | None = None
    launched_at: datetime | None = None
    website: str | None = None
    logo_url: str | None = None
    reviews: list[ReviewData] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
