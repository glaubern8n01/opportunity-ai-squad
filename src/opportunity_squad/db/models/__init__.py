"""Importa todos os modelos para popular Base.metadata (necessário para autogenerate do Alembic)."""

from opportunity_squad.db.models.analysis import Analysis
from opportunity_squad.db.models.competitor import Competitor
from opportunity_squad.db.models.ideation import Feature, Idea, MvpProject, Roadmap
from opportunity_squad.db.models.market import MarketAnalysis, TrendAnalysis
from opportunity_squad.db.models.ops import AgentLog, Run
from opportunity_squad.db.models.product import Product, ProductVersion
from opportunity_squad.db.models.report import Alert, Report
from opportunity_squad.db.models.review import Review
from opportunity_squad.db.models.source import Source, SourcesLog
from opportunity_squad.db.models.taxonomy import Category, Tag, product_tags
from opportunity_squad.db.models.user import Favorite, Watchlist

__all__ = [
    "Analysis",
    "Competitor",
    "Feature",
    "Idea",
    "MvpProject",
    "Roadmap",
    "MarketAnalysis",
    "TrendAnalysis",
    "AgentLog",
    "Run",
    "Product",
    "ProductVersion",
    "Alert",
    "Report",
    "Review",
    "Source",
    "SourcesLog",
    "Category",
    "Tag",
    "product_tags",
    "Favorite",
    "Watchlist",
]
