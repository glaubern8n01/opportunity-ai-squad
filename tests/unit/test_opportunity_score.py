import pytest

from opportunity_squad.scoring.opportunity_score import calculate_opportunity_score

_ALL_TENS = {
    "market": 10,
    "competition": 10,
    "estimated_revenue": 10,
    "reviews": 10,
    "users_and_downloads": 10,
    "trend": 10,
    "dev_ease": 10,
    "ai_potential": 10,
    "automation_potential": 10,
    "scalability": 10,
    "complexity_penalty": 10,
    "monetization_chance": 10,
    "virality_chance": 10,
}


def test_all_tens_yields_perfect_score():
    result = calculate_opportunity_score(_ALL_TENS)
    assert result.final_score == 10.0


def test_all_zeros_yields_zero_score():
    zeros = dict.fromkeys(_ALL_TENS, 0)
    result = calculate_opportunity_score(zeros)
    assert result.final_score == 0.0


def test_missing_criteria_raises():
    incomplete = dict(_ALL_TENS)
    del incomplete["market"]
    with pytest.raises(ValueError, match="market"):
        calculate_opportunity_score(incomplete)


def test_breakdown_matches_input():
    result = calculate_opportunity_score(_ALL_TENS)
    assert result.market == 10
    assert result.virality_chance == 10
