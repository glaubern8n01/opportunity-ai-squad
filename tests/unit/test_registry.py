import pytest
from plugins.registry import discover, discover_all, load_plugin

from opportunity_squad.core.exceptions import PluginNotFoundError


def test_discover_finds_known_source_plugins():
    manifests = discover("sources")
    assert "github_trending" in manifests
    assert "hacker_news" in manifests


def test_discover_unknown_category_returns_empty():
    assert discover("not_a_real_category") == {}


def test_discover_all_covers_every_category():
    manifests = discover_all()
    assert set(manifests) == {"sources", "ai", "notifications", "reports", "exports"}


def test_load_plugin_raises_for_unknown_name():
    with pytest.raises(PluginNotFoundError):
        load_plugin("sources", "does_not_exist")


def test_load_plugin_instantiates_and_initializes():
    connector = load_plugin("sources", "hacker_news")
    assert connector.name == "hacker_news"
    connector.shutdown()
