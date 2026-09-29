"""Unit tests for Query Complexity & Agent-Necessity Router."""
import pytest
from backend.agents.router import QueryComplexityRouter

@pytest.fixture
def router():
    return QueryComplexityRouter()

def test_lookup_routing(router):
    # Direct lookup question -> agent not required
    q = "Who won the men's 100 metres at the 2008 Summer Olympics?"
    res = router.route(q)
    assert res["query_type"] == "lookup"
    assert res["agent_required"] is False
    assert res["recommended_pipeline"] == "rag"

def test_aggregation_routing(router):
    # Aggregation question -> agent required
    q = "According to the provided corpus, how many biathlon events at the 2018 Winter Olympics had more than 73 competitors?"
    res = router.route(q)
    assert res["query_type"] == "aggregation"
    assert res["agent_required"] is True
    assert res["recommended_pipeline"] == "agentic"

def test_temporal_routing(router):
    # Temporal question -> agent required
    q = "Who won the gold medal in the event held at the Summer Olympics held immediately before 2016?"
    res = router.route(q)
    assert res["query_type"] == "temporal"
    assert res["agent_required"] is True
    assert res["recommended_pipeline"] == "agentic"

def test_superlative_routing(router):
    # Superlative question -> agent required
    q = "Which athletics event at the 2008 Summer Olympics had the highest number of competitors?"
    res = router.route(q)
    assert res["query_type"] == "superlative"
    assert res["agent_required"] is True
    assert res["recommended_pipeline"] == "agentic"

def test_multihop_routing(router):
    # Multi-hop question -> agent required
    q = "Who won the gold medal in the event held at Olympic Weightlifting Gymnasium on 20 September 1988?"
    res = router.route(q)
    assert res["query_type"] == "multi_hop"
    assert res["agent_required"] is True
    assert res["recommended_pipeline"] == "agentic"