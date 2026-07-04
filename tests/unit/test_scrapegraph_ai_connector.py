import pytest
import respx
from httpx import Response
from plugins.sources.scrapegraph_ai.connector import ScrapeGraphAIConnector

from opportunity_squad.core.exceptions import SourceFetchError

_BASE = "https://v2-api.scrapegraphai.com/api"


def _connector() -> ScrapeGraphAIConnector:
    connector = ScrapeGraphAIConnector()
    connector.initialize({"api_key": "sgai-test-key"})
    return connector


@respx.mock
def test_search_normalizes_results():
    respx.post(f"{_BASE}/search").mock(
        return_value=Response(
            200,
            json={
                "results": [
                    {
                        "url": "https://example.com/product-x",
                        "title": "Product X",
                        "content": "a cool product",
                    }
                ],
                "json": {
                    "products": [
                        {
                            "name": "Product X",
                            "tagline": "Do X faster",
                            "url": "https://example.com/product-x",
                            "pricing_model": "freemium",
                            "has_free_plan": True,
                            "category": "productivity",
                        }
                    ]
                },
                "metadata": {"search": {}, "pages": {}},
            },
        )
    )

    connector = _connector()
    products = connector.search("ferramentas de produtividade")
    connector.shutdown()

    assert len(products) == 1
    product = products[0]
    assert product.source == "scrapegraph_ai"
    assert product.external_id == "https://example.com/product-x"
    assert product.name == "Product X"
    assert product.pricing_model == "freemium"
    assert product.has_free_plan is True


@respx.mock
def test_search_uses_default_query_when_none_given():
    route = respx.post(f"{_BASE}/search").mock(
        return_value=Response(
            200,
            json={"results": [], "json": {"products": []}, "metadata": {"search": {}, "pages": {}}},
        )
    )

    connector = _connector()
    products = connector.search()
    connector.shutdown()

    assert products == []
    sent_body = route.calls[0].request.content
    assert b"novos produtos SaaS" in sent_body


@respx.mock
def test_fetch_details_extracts_single_product_by_url():
    url = "https://example.com/product-y"
    respx.post(f"{_BASE}/extract").mock(
        return_value=Response(
            200,
            json={
                "raw": None,
                "json": {"products": [{"name": "Product Y", "tagline": "Y things"}]},
                "usage": {"promptTokens": 10, "completionTokens": 5},
                "metadata": {},
            },
        )
    )

    connector = _connector()
    product = connector.fetch_details(url)
    connector.shutdown()

    assert product.name == "Product Y"
    assert product.external_id == url


def test_fetch_details_rejects_non_url_external_id():
    connector = _connector()
    with pytest.raises(SourceFetchError):
        connector.fetch_details("not-a-url")
    connector.shutdown()


def test_fetch_reviews_returns_empty_for_non_url_external_id():
    connector = _connector()
    assert connector.fetch_reviews("not-a-url") == []
    connector.shutdown()


@respx.mock
def test_fetch_reviews_normalizes_testimonials():
    url = "https://example.com/product-z"
    respx.post(f"{_BASE}/extract").mock(
        return_value=Response(
            200,
            json={
                "raw": None,
                "json": {
                    "reviews": [
                        {"author": "Jane", "body": "Great tool", "rating": 5},
                        {"author": None, "body": "", "rating": None},
                    ]
                },
                "usage": {"promptTokens": 10, "completionTokens": 5},
                "metadata": {},
            },
        )
    )

    connector = _connector()
    reviews = connector.fetch_reviews(url)
    connector.shutdown()

    assert len(reviews) == 1
    assert reviews[0].author == "Jane"
    assert reviews[0].body == "Great tool"


def test_normalize_falls_back_to_synthetic_id_without_url():
    connector = _connector()
    product = connector.normalize({"name": "No URL Product"})
    connector.shutdown()

    assert product.external_id.startswith("sha256:")
    assert product.name == "No URL Product"
