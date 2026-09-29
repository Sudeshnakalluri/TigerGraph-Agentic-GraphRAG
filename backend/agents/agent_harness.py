"""Agent Execution Trace and State Harness."""
import time
from typing import Dict, List, Any, Optional

class AgentHarness:
    """Manages observable agent execution trace and cost accounting."""

    def __init__(self, query: str, query_type: str, agent_required: bool):
        self.query = query
        self.query_type = query_type
        self.agent_required = agent_required
        self.steps: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.tool_calls_count = 0
        self.graph_queries_count = 0
        self.graph_hops_count = 0
        self.llm_calls_count = 0
        self.context_tokens = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def add_step(self, action: str, description: str, status: str = "success", details: Optional[Dict[str, Any]] = None):
        """Records an observable action into the structured trace."""
        step_num = len(self.steps) + 1
        elapsed = round((time.time() - self.start_time) * 1000, 2)
        step_obj = {
            "step": step_num,
            "action": action,
            "description": description,
            "status": status,
            "elapsed_ms": elapsed
        }
        if details:
            step_obj["details"] = details
        self.steps.append(step_obj)

    def record_tool_call(self, tool_name: str):
        self.tool_calls_count += 1

    def record_graph_query(self, hops: int = 1):
        self.graph_queries_count += 1
        self.graph_hops_count += hops

    def record_llm_call(self, in_tokens: int, out_tokens: int):
        self.llm_calls_count += 1
        self.input_tokens += in_tokens
        self.output_tokens += out_tokens

    def get_trace(self) -> Dict[str, Any]:
        """Returns structured observable trace."""
        total_time = round((time.time() - self.start_time) * 1000, 2)
        return {
            "query": self.query,
            "query_type": self.query_type,
            "agent_required": self.agent_required,
            "total_steps": len(self.steps),
            "execution_time_ms": total_time,
            "tool_calls": self.tool_calls_count,
            "graph_queries": self.graph_queries_count,
            "graph_hops": self.graph_hops_count,
            "llm_calls": self.llm_calls_count,
            "tokens": {
                "context_tokens": self.context_tokens,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "total_tokens": self.context_tokens + self.input_tokens + self.output_tokens
            },
            "steps": self.steps
        }