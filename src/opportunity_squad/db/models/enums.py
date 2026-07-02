"""Enums Python usados pelas colunas Enum das tabelas (armazenados como texto no Postgres)."""

from __future__ import annotations

import enum


class ProductStatus(enum.StrEnum):
    ACTIVE = "active"
    PROMISING = "promising"
    DECLINING = "declining"
    ARCHIVED = "archived"


class RunStatus(enum.StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class SourceLogStatus(enum.StrEnum):
    SUCCESS = "success"
    ERROR = "error"


class ReportPeriodEnum(enum.StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AlertLevel(enum.StrEnum):
    INFO = "info"
    OPPORTUNITY = "opportunity"
    REPORT = "report"
    ERROR = "error"


class IdeaStatus(enum.StrEnum):
    NEW = "new"
    RESEARCHING = "researching"
    VALIDATED = "validated"
    DISCARDED = "discarded"
    IN_PROGRESS = "in_progress"


class MvpStatus(enum.StrEnum):
    PLANNING = "planning"
    BUILDING = "building"
    LAUNCHED = "launched"
    PAUSED = "paused"


class FeaturePriority(enum.StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FeatureStatus(enum.StrEnum):
    BACKLOG = "backlog"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class SentimentLabel(enum.StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class TrendDirection(enum.StrEnum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
