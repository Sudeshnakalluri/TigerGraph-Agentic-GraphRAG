"""Pipeline 3: Agentic GraphRAG (Router + Orchestrator + Specialized Tools + Grounding)."""
import time
from typing import Dict, List, Any, Optional
from backend.agents.orchestrator import AgentOrchestrator
from backend.graph.graph_service import GraphService

class AgenticGraphRAGPipeline:
    """Autonomous Agentic GraphRAG pipeline with dynamic planning and observable trace."""

    def __init__(self, orchestrator: Optional[AgentOrchestrator] = None, graph_service: Optional[GraphService] = None):
        self.orchestrator = orchestrator or AgentOrchestrator()
        self.graph = graph_service or GraphService()

    def run(self, query: str) -> Dict[str, Any]:
        """Runs the orchestrator agent and returns answer, trace, and cost metrics."""
        result = self.orchestrator.run(query)
        trace = result["trace"]

        return {
            "pipeline": "Agentic GraphRAG",
            "backend": self.graph.backend_name,
            "query": query,
            "query_type": result["query_type"],
            "agent_required": result["agent_required"],
            "answer": result["answer"],
            "citations": result["citations"],
            "evidence": result["evidence"],
            "validation": result["validation"],
            "trace": trace,
            "metrics": {
                "latency_ms": trace["execution_time_ms"],
                "tool_calls": trace["tool_calls"],
                "graph_hops": trace["graph_hops"],
                "graph_queries": trace["graph_queries"],
                "llm_calls": trace["llm_calls"],
                "context_tokens": trace["tokens"]["context_tokens"],
                "input_tokens": trace["tokens"]["input_tokens"],
                "output_tokens": trace["tokens"]["output_tokens"],
                "total_tokens": trace["tokens"]["total_tokens"]
            }
        }