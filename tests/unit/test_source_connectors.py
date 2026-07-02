import respx
from httpx import Response
from plugins.sources.github_trending.connector import GitHubTrendingConnector
from plugins.sources.hacker_news.connector import HackerNewsConnector


@respx.mock
def test_github_trending_search_normalizes_results():
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=Response(
            200,
            json={
                "items": [
                    {
                        "full_name": "owner/repo",
                        "name": "repo",
                        "description": "a cool project",
                        "html_url": "https://github.com/owner/repo",
                        "language": "Python",
                        "topics": ["ai", "saas"],
                        "stargazers_count": 42,
                        "homepage": None,
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ]
            },
        )
    )

    connector = GitHubTrendingConnector()
    connector.initialize({})
    products = connector.search()
    connector.shutdown()

    assert len(products) == 1
    product = products[0]
    assert product.source == "github_trending"
    assert product.external_id == "owner/repo"
    assert product.upvotes == 42
    assert product.tags == ["ai", "saas"]


@respx.mock
def test_hacker_news_fetch_details_normalizes():
    respx.get("https://hacker-news.firebaseio.com/v0/item/1.json").mock(
        return_value=Response(
            200,
            json={
                "id": 1,
                "title": "Show HN: cool thing",
                "url": "https://example.com",
                "score": 99,
                "time": 1700000000,
            },
        )
    )

    connector = HackerNewsConnector()
    connector.initialize({})
    product = connector.fetch_details("1")
    connector.shutdown()

    assert product.external_id == "1"
    assert product.name == "Show HN: cool thing"
    assert product.upvotes == 99
