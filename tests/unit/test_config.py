import pytest
from pydantic import ValidationError

from opportunity_squad.core.config import Settings


def test_database_url_is_required(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_csv_plugin_lists_are_parsed(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setenv("ENABLED_SOURCE_PLUGINS", "github_trending, hacker_news,, reddit")
    settings = Settings(_env_file=None)
    assert settings.enabled_source_plugins == ["github_trending", "hacker_news", "reddit"]


def test_empty_plugin_list_defaults_to_empty(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.delenv("ENABLED_SOURCE_PLUGINS", raising=False)
    settings = Settings(_env_file=None)
    assert settings.enabled_source_plugins == []


def test_is_production_property(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setenv("APP_ENV", "production")
    settings = Settings(_env_file=None)
    assert settings.is_production is True
