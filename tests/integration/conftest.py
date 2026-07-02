"""Fixtures de integração: rodam contra o Postgres real definido em DATABASE_URL (.env).

Requer `docker compose up -d postgres` com as migrations aplicadas (`alembic upgrade head`).
"""

from __future__ import annotations

import pytest
from sqlalchemy import text

from opportunity_squad.db.session import get_engine

_TABLES_TO_CLEAN = (
    "product_versions",
    "reviews",
    "competitors",
    "market_analysis",
    "analyses",
    "product_tags",
    "products",
    "sources",
    "runs",
    "agent_logs",
)


@pytest.fixture(autouse=True)
def _clean_database():
    yield
    engine = get_engine()
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {', '.join(_TABLES_TO_CLEAN)} RESTART IDENTITY CASCADE"))
