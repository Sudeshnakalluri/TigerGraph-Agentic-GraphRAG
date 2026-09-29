"""Standalone Test Runner for TigerGraph Hackathon backend tests."""
import sys
import io
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_router():
    print("Testing QueryComplexityRouter...")
    from backend.agents.router import QueryComplexityRouter
    router = QueryComplexityRouter()
    
    # 1. Lookup
    r1 = router.route("Who won the men's 100 metres at the 2008 Summer Olympics?")
    assert r1["query_type"] == "lookup", f"Expected lookup, got {r1['query_type']}"
    assert r1["agent_required"] is False, "Expected agent_required=False"
    
    # 2. Aggregation
    r2 = router.route("According to the provided corpus, how many biathlon events at the 2018 Winter Olympics had more than 73 competitors?")
    assert r2["query_type"] == "aggregation", f"Expected aggregation, got {r2['query_type']}"
    assert r2["agent_required"] is True, "Expected agent_required=True"
    
    # 3. Temporal
    r3 = router.route("Who won the gold medal in the event held at the Summer Olympics held immediately before 2016?")
    assert r3["query_type"] == "temporal", f"Expected temporal, got {r3['query_type']}"
    assert r3["agent_required"] is True, "Expected agent_required=True"

    # 4. Superlative
    r4 = router.route("Which athletics event at the 2008 Summer Olympics had the highest number of competitors?")
    assert r4["query_type"] == "superlative", f"Expected superlative, got {r4['query_type']}"
    assert r4["agent_required"] is True, "Expected agent_required=True"

    # 5. Multi-Hop
    r5 = router.route("Who won the gold medal in the event held at Olympic Tennis Centre on 15 to 22 August 2004?")
    assert r5["query_type"] == "multi_hop", f"Expected multi_hop, got {r5['query_type']}"
    assert r5["agent_required"] is True, "Expected agent_required=True"
    print("  [PASS] QueryComplexityRouter: ALL 5 ARCHETYPES PASSED")

def test_graph():
    print("Testing GraphService & KnowledgeGraph...")
    from backend.graph.graph_service import GraphService
    gs = GraphService()
    
    status = gs.get_status()
    assert status["graph_nodes"] > 1000, f"Expected >1000 nodes, got {status['graph_nodes']}"
    assert status["graph_edges"] > 1000, f"Expected >1000 edges, got {status['graph_edges']}"
    
    # Temporal navigation
    prev = gs.get_temporal_edition("2016 Summer", direction="previous")
    assert prev is not None, "Temporal navigation returned None"
    assert "2012" in prev.get("name", ""), f"Expected 2012, got {prev.get('name')}"

    # Aggregation
    evs = gs.get_events_by_competitors(games_filter="2018 Winter", sport_filter="Biathlon", min_competitors=73, operator=">")
    assert len(evs) == 5, f"Expected 5 events, got {len(evs)}"

    # Superlative
    sup = gs.get_superlative(games_filter="2008 Summer", sport_filter="Athletics", metric="competitors", order="DESC")
    assert sup is not None, "Superlative query returned None"
    print("  [PASS] GraphService: Temporal, Aggregation & Superlative PASSED")

def test_pipelines():
    print("Testing Three Pipelines & Comparator...")
    from backend.pipelines.comparator import PipelineComparator
    comparator = PipelineComparator()

    # RAG
    q = "Who won the men's 100 metres at the 2008 Summer Olympics?"
    rag_res = comparator.rag.run(q)
    assert rag_res["pipeline"] == "Standard RAG"
    assert "answer" in rag_res
    assert rag_res["metrics"]["total_tokens"] > 0

    # GraphRAG
    grag_res = comparator.graphrag.run(q)
    assert grag_res["pipeline"] == "GraphRAG"
    assert "answer" in grag_res

    # Agentic GraphRAG
    q_agg = "According to the provided corpus, how many biathlon events at the 2018 Winter Olympics had more than 73 competitors?"
    agent_res = comparator.agentic.run(q_agg)
    assert agent_res["pipeline"] == "Agentic GraphRAG"
    assert agent_res["answer"] == "5", f"Expected '5', got {agent_res['answer']}"
    assert agent_res["agent_required"] is True

    # Side by side comparison
    comp = comparator.compare(q_agg)
    assert "pipelines" in comp
    assert "overhead" in comp
    print("  [PASS] Pipelines & Comparator: RAG, GraphRAG & Agentic PASSED")

def test_harness_and_trace():
    print("Testing AgentHarness Trace...")
    from backend.agents.agent_harness import AgentHarness
    harness = AgentHarness("Test query", "aggregation", True)
    harness.add_step("test_action", "Test description", details={"info": "ok"})
    harness.record_tool_call("AggregationTool")
    harness.record_graph_query(hops=2)
    harness.record_llm_call(in_tokens=50, out_tokens=5)
    
    trace = harness.get_trace()
    assert trace["total_steps"] == 1
    assert trace["tool_calls"] == 1
    assert trace["graph_hops"] == 2
    assert trace["tokens"]["total_tokens"] == 55
    print("  [PASS] AgentHarness Trace: PASSED")

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING TIGERGRAPH AGENTIC GRAPHRAG VERIFICATION SUITE")
    print("=" * 60)
    try:
        test_router()
        test_graph()
        test_pipelines()
        test_harness_and_trace()
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED! (4/4 TEST SUITES)")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n[FAIL] Test assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
