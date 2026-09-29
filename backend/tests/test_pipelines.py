"""Unit tests for the Three Pipelines (RAG, GraphRAG, Agentic GraphRAG) and Comparator."""
import pytest
from backend.pipelines.rag_pipeline import StandardRAGPipeline
from backend.pipelines.graphrag_pipeline import GraphRAGPipeline
from backend.pipelines.agentic_graphrag_pipeline import AgenticGraphRAGPipeline
from backend.pipelines.comparator import PipelineComparator

@pytest.fixture
def comparator():
    return PipelineComparator()

def test_pipeline_1_rag(comparator):
    # Lookup query
    q = "Who won the men's marathon at the 2008 Summer Olympics?"
    res = comparator.rag.run(q)
    assert res["pipeline"] == "Standard RAG"
    assert "answer" in res
    assert res["metrics"]["tool_calls"] == 1
    assert res["metrics"]["total_tokens"] > 0
    assert res["metrics"]["latency_ms"] > 0

def test_pipeline_2_graphrag(comparator):
    q = "Who won the men's marathon at the 2008 Summer Olympics?"
    res = comparator.graphrag.run(q)
    assert res["pipeline"] == "GraphRAG"
    assert "answer" in res
    assert res["metrics"]["tool_calls"] == 2
    assert "backend" in res

def test_pipeline_3_agentic(comparator):
    # Aggregation query
    q = "According to the provided corpus, how many biathlon events at the 2018 Winter Olympics had more than 73 competitors?"
    res = comparator.agentic.run(q)
    assert res["pipeline"] == "Agentic GraphRAG"
    assert res["answer"] == "5"
    assert res["query_type"] == "aggregation"
    assert res["agent_required"] is True
    assert "trace" in res
    assert len(res["trace"]["steps"]) >= 3

def test_comparator_side_by_side(comparator):
    q = "Who won the gold medal in the event held at Olympic Weightlifting Gymnasium on 20 September 1988?"
    res = comparator.compare(q, expected_answer="Naim Süleymanoğlu")
    assert "pipelines" in res
    assert "rag" in res["pipelines"]
    assert "graphrag" in res["pipelines"]
    assert "agentic" in res["pipelines"]
    assert "overhead" in res
    assert "latency_overhead_ms" in res["overhead"]
    assert "token_overhead" in res["overhead"]