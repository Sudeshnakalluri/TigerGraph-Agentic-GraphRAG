"""Comparator: Executes Standard RAG, GraphRAG, and Agentic GraphRAG Side-by-Side."""
from typing import Dict, Any, Optional
from backend.pipelines.rag_pipeline import StandardRAGPipeline
from backend.pipelines.graphrag_pipeline import GraphRAGPipeline
from backend.pipelines.agentic_graphrag_pipeline import AgenticGraphRAGPipeline

class PipelineComparator:
    """Runs all three pipelines on the identical query and compares accuracy, tokens, and latency."""

    def __init__(self):
        self.rag = StandardRAGPipeline()
        self.graphrag = GraphRAGPipeline()
        self.agentic = AgenticGraphRAGPipeline()

    def compare(self, query: str, expected_answer: Optional[str] = None) -> Dict[str, Any]:
        """Runs the 3 pipelines and computes side-by-side comparison and overhead metrics."""
        # Execute Pipeline 1
        rag_res = self.rag.run(query)

        # Execute Pipeline 2
        graphrag_res = self.graphrag.run(query)

        # Execute Pipeline 3
        agentic_res = self.agentic.run(query)

        # Compute Agent Overhead
        latency_overhead_ms = round(agentic_res["metrics"]["latency_ms"] - rag_res["metrics"]["latency_ms"], 2)
        token_overhead = agentic_res["metrics"]["total_tokens"] - rag_res["metrics"]["total_tokens"]

        return {
            "query": query,
            "query_type": agentic_res["query_type"],
            "agent_required": agentic_res["agent_required"],
            "graph_backend": agentic_res["backend"],
            "expected_answer": expected_answer,
            "pipelines": {
                "rag": rag_res,
                "graphrag": graphrag_res,
                "agentic": agentic_res
            },
            "overhead": {
                "latency_overhead_ms": latency_overhead_ms,
                "token_overhead": token_overhead,
                "agent_tool_calls": agentic_res["metrics"]["tool_calls"],
                "agent_graph_hops": agentic_res["metrics"]["graph_hops"]
            }
        }