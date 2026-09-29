"""Query Complexity & Agent-Necessity Router.

Classifies incoming queries into:
- lookup
- multi_hop
- temporal
- aggregation
- superlative

Determines whether agentic reasoning is necessary (agent_required: True/False).
Aligns with the Hackathon Thesis:
"Figure out which questions need an agent, and which don't."
"""
import re
from typing import Dict, Any

class QueryComplexityRouter:
    """Classifies queries and routes to Standard RAG or Agentic GraphRAG."""

    def route(self, query: str) -> Dict[str, Any]:
        """Analyzes query complexity and returns routing decision."""
        q = query.lower().strip()

        # 1. Temporal: edition-to-edition relationships (PREVIOUS_EDITION, NEXT_EDITION)
        temporal_patterns = [
            r"\bimmediately before\b", r"\bimmediately after\b",
            r"\bprior edition\b", r"\bsubsequent edition\b",
            r"\bheld before\b", r"\bheld after\b",
            r"\bfollowing year\b", r"\bpreceding edition\b",
            r"\bnext edition\b", r"\bprevious edition\b"
        ]
        if any(re.search(p, q) for p in temporal_patterns):
            return {
                "query_type": "temporal",
                "agent_required": True,
                "reason": "Query requires temporal traversal across Olympic editions (PREVIOUS_EDITION/NEXT_EDITION).",
                "recommended_pipeline": "agentic"
            }

        # 2. Multi-Hop: connects Venue, Date, Event, and Athlete entities
        multihop_indicators = [
            r"held at.*on\s+\d+", r"venue.*on\s+\d+", r"gymnasium on\s+\d+",
            r"stadium on\s+\d+", r"centre on\s+\d+", r"participated in.*and later",
            r"won.*and.*also", r"both.*and", r"event held at"
        ]
        if any(re.search(p, q) for p in multihop_indicators):
            return {
                "query_type": "multi_hop",
                "agent_required": True,
                "reason": "Query requires multi-hop path traversal connecting Venue, Date, Event, and Athlete entities.",
                "recommended_pipeline": "agentic"
            }

        # 3. Superlative: maximum, minimum, highest, lowest ranking across entities
        superlative_patterns = [
            r"\bhighest\b", r"\blowest\b", r"\bmost\b", r"\bfewest\b",
            r"\bmaximum\b", r"\bminimum\b", r"\blargest\b", r"\bsmallest\b"
        ]
        if any(re.search(p, q) for p in superlative_patterns):
            return {
                "query_type": "superlative",
                "agent_required": True,
                "reason": "Query requires superlative ranking and comparison across all candidate events.",
                "recommended_pipeline": "agentic"
            }

        # 4. Single-Event Fact Lookup (e.g. "How many nations competed in Sailing at the 2016 Summer Olympics - Women's RS:X?")
        # Infobox / direct fact lookup in a single event document
        if re.search(r"how many (?:nations|competitors|athletes|countries) competed in", q):
            return {
                "query_type": "lookup",
                "agent_required": False,
                "reason": "Single event factual lookup directly retrievable from the event document infobox without agent orchestration.",
                "recommended_pipeline": "rag"
            }

        # 5. Direct Fact Lookup patterns
        direct_lookup_patterns = [
            r"\bwho hosted\b", r"\bwhich city hosted\b", r"\bwhat venue\b",
            r"\bwhere was\b", r"\bwhen was\b", r"\bwho won the gold medal in the \d{4}\b"
        ]
        if any(re.search(p, q) for p in direct_lookup_patterns) and not any(re.search(p, q) for p in [r"immediately", r"before", r"after"]):
            return {
                "query_type": "lookup",
                "agent_required": False,
                "reason": "Direct factual lookup answerable via standard semantic search without multi-step reasoning.",
                "recommended_pipeline": "rag"
            }

        # 6. Aggregation: multi-event or cross-edition counting and comparisons
        agg_patterns = [
            r"\bhow many\b", r"\bcount\b", r"\btotal number\b",
            r"\bmore than\b", r"\bfewer than\b", r"\bgreater than\b",
            r"\bless than\b", r"\bexceeded\b", r"\bcombined\b", r"\bacross\b"
        ]
        if any(re.search(p, q) for p in agg_patterns):
            return {
                "query_type": "aggregation",
                "agent_required": True,
                "reason": "Query requires counting, filtering, or aggregating across multiple event/athlete records.",
                "recommended_pipeline": "agentic"
            }

        # 7. Default: Direct Lookup
        return {
            "query_type": "lookup",
            "agent_required": False,
            "reason": "Direct factual lookup answerable via standard semantic search without multi-step reasoning.",
            "recommended_pipeline": "rag"
        }
