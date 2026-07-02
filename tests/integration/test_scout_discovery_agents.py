from opportunity_squad.agents.discovery_agent import DiscoveryAgent
from opportunity_squad.agents.scout_agent import ScoutAgent
from opportunity_squad.core.entities.product import NormalizedProduct
from opportunity_squad.core.interfaces.agent import AgentContext
from opportunity_squad.core.interfaces.source import SourceConnector
from opportunity_squad.db.models.product import Product
from opportunity_squad.db.session import session_scope


class FakeSourceConnector(SourceConnector):
    name = "fake_source"

    def initialize(self, config):
        pass

    def search(self, query=None, **kwargs):
        return [
            NormalizedProduct(
                source=self.name,
                external_id="p1",
                name="Product One",
                upvotes=500,
                users_count=20_000,
            ),
            NormalizedProduct(
                source=self.name,
                external_id="p2",
                name="Product Two",
                upvotes=1,
            ),
        ]

    def fetch_details(self, external_id):
        raise NotImplementedError

    def fetch_reviews(self, external_id):
        return []

    def normalize(self, raw):
        raise NotImplementedError


def test_scout_agent_persists_new_products():
    scout = ScoutAgent({"fake_source": FakeSourceConnector()})
    result = scout.run(AgentContext(run_id="test-scout"))

    assert result.success
    assert result.output["discovered"] == 2

    with session_scope() as session:
        names = {p.name for p in session.query(Product).all()}
    assert names == {"Product One", "Product Two"}


def test_scout_agent_upserts_on_second_run():
    scout = ScoutAgent({"fake_source": FakeSourceConnector()})
    scout.run(AgentContext(run_id="run-1"))
    scout.run(AgentContext(run_id="run-2"))

    with session_scope() as session:
        count = session.query(Product).count()
    assert count == 2  # não duplica


def test_discovery_agent_scores_products_by_metrics():
    ScoutAgent({"fake_source": FakeSourceConnector()}).run(AgentContext(run_id="test-scout"))
    result = DiscoveryAgent(min_score=3.0).run(AgentContext(run_id="test-discovery"))

    assert result.success
    assert result.output["qualified"] == 1  # só "Product One" passa do threshold

    with session_scope() as session:
        scores = {p.name: p.opportunity_score for p in session.query(Product).all()}
    assert scores["Product One"] > scores["Product Two"]
