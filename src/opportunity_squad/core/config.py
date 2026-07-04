"""Configuração central da aplicação. Toda variável obrigatória é validada aqui (fail-fast)."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _split_csv(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return value
    return [item.strip() for item in value.split(",") if item.strip()]


CsvList = Annotated[list[str], NoDecode]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = Field(default="opportunity-ai-squad", alias="APP_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    timezone: str = Field(default="America/Sao_Paulo", alias="TIMEZONE")

    # Database
    database_url: str = Field(alias="DATABASE_URL")
    supabase_url: str | None = Field(default=None, alias="SUPABASE_URL")
    supabase_anon_key: str | None = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str | None = Field(
        default=None, alias="SUPABASE_SERVICE_ROLE_KEY"
    )

    # AI provider
    ai_provider: str = Field(default="anthropic", alias="AI_PROVIDER")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-5", alias="ANTHROPIC_MODEL")
    anthropic_model_cheap: str = Field(
        default="claude-haiku-4-5", alias="ANTHROPIC_MODEL_CHEAP"
    )
    anthropic_model_deep: str = Field(default="claude-opus-4-8", alias="ANTHROPIC_MODEL_DEEP")

    # Telegram
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(default=None, alias="TELEGRAM_CHAT_ID")

    # Fontes de dados
    github_token: str | None = Field(default=None, alias="GITHUB_TOKEN")
    scrapegraph_api_key: str | None = Field(default=None, alias="SCRAPEGRAPH_API_KEY")

    # Plugins
    enabled_source_plugins: CsvList = Field(default_factory=list, alias="ENABLED_SOURCE_PLUGINS")
    enabled_ai_plugins: CsvList = Field(default_factory=list, alias="ENABLED_AI_PLUGINS")
    enabled_notification_plugins: CsvList = Field(
        default_factory=list, alias="ENABLED_NOTIFICATION_PLUGINS"
    )
    enabled_report_plugins: CsvList = Field(default_factory=list, alias="ENABLED_REPORT_PLUGINS")

    # Scheduler
    scan_interval_minutes: int = Field(default=60, alias="SCAN_INTERVAL_MINUTES")
    daily_report_hour: int = Field(default=8, alias="DAILY_REPORT_HOUR")
    weekly_report_day: str = Field(default="mon", alias="WEEKLY_REPORT_DAY")
    monthly_report_day: int = Field(default=1, alias="MONTHLY_REPORT_DAY")

    @field_validator(
        "enabled_source_plugins",
        "enabled_ai_plugins",
        "enabled_notification_plugins",
        "enabled_report_plugins",
        mode="before",
    )
    @classmethod
    def _parse_csv(cls, value: str | list[str]) -> list[str]:
        return _split_csv(value)

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância singleton de Settings, validando variáveis obrigatórias uma única vez."""
    return Settings()  # type: ignore[call-arg]  # campos obrigatórios vêm do .env em runtime
