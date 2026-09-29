"""Unit tests for Agent Orchestrator, Tools, and Observable Trace."""
import pytest
from backend.agents.orchestrator import AgentOrchestrator

@pytest.fixture
def orchestrator():
    return AgentOrchestrator()

def test_orchestrator_aggregation(orchestrator):
    q = "According to the provided corpus, how many biathlon events at the 2018 Winter Olympics had more than 73 competitors?"
    res = orchestrator.run(q)
    assert res["query_type"] == "aggregation"
    assert res["agent_required"] is True
    assert res["answer"] == "5"
    assert len(res["trace"]["steps"]) >= 3
    assert res["trace"]["tool_calls"] > 0

def test_orchestrator_trace_structure(orchestrator):
    q = "Who won the gold medal in the event held at Olympic Weightlifting Gymnasium on 20 September 1988?"
    res = orchestrator.run(q)
    trace = res["trace"]
    assert "query" in trace
    assert "query_type" in trace
    assert "execution_time_ms" in trace
    assert "steps" in trace
    assert len(trace["steps"]) >= 3
    # Verify observable step fields
    for step in trace["steps"]:
        assert "step" in step
        assert "action" in step
        assert "description" in step
        assert "status" in step