"""Do insight à execução: ideias validadas, roadmap, projetos de MVP e suas features."""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from opportunity_squad.db.base import Base, TimestampMixin
from opportunity_squad.db.models.enums import FeaturePriority, FeatureStatus, IdeaStatus, MvpStatus


class Idea(Base, TimestampMixin):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    based_on_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    opportunity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[IdeaStatus] = mapped_column(default=IdeaStatus.NEW, index=True)


class Roadmap(Base, TimestampMixin):
    __tablename__ = "roadmaps"

    id: Mapped[int] = mapped_column(primary_key=True)
    idea_id: Mapped[int | None] = mapped_column(
        ForeignKey("ideas.id", ondelete="CASCADE"), nullable=True
    )
    mvp_project_id: Mapped[int | None] = mapped_column(
        ForeignKey("mvp_projects.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    milestones: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)


class MvpProject(Base, TimestampMixin):
    __tablename__ = "mvp_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    idea_id: Mapped[int | None] = mapped_column(
        ForeignKey("ideas.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255))
    stack: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[MvpStatus] = mapped_column(default=MvpStatus.PLANNING, index=True)
    repo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Feature(Base, TimestampMixin):
    __tablename__ = "features"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=True
    )
    mvp_project_id: Mapped[int | None] = mapped_column(
        ForeignKey("mvp_projects.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[FeaturePriority | None] = mapped_column(nullable=True)
    status: Mapped[FeatureStatus] = mapped_column(default=FeatureStatus.BACKLOG, index=True)
