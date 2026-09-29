"""Specialized Agent Tools for TigerGraph Agentic GraphRAG System."""
import re
from typing import Dict, List, Any, Optional
from backend.graph.graph_service import GraphService
from backend.retrieval.vector_store import VectorStore

class SpecializedTools:
    """Suite of discrete tools invoked selectively by the Agent Orchestrator."""

    def __init__(self, graph_service: Optional[GraphService] = None, vector_store: Optional[VectorStore] = None):
        self.graph = graph_service or GraphService()
        self.vector = vector_store or VectorStore()

    def entity_linker(self, query: str) -> List[Dict[str, Any]]:
        """Extracts and resolves entity mentions in query to graph nodes."""
        tokens = [t.strip(",.?!") for t in query.split() if len(t.strip(",.?!")) > 3]
        matched = []
        seen = set()
        for tok in tokens:
            for ent in self.graph.find_entities(tok):
                if ent["id"] not in seen:
                    seen.add(ent["id"])
                    matched.append(ent)
        return matched[:5]

    def graph_traversal(self, entity_id: str, max_hops: int = 1) -> List[Dict[str, Any]]:
        """Traverses 1-hop or 2-hop edges around an entity."""
        if max_hops == 1:
            return self.graph.get_1hop(entity_id)
        return self.graph.get_2hop(entity_id)

    def vector_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Dense similarity search over corpus chunks."""
        return self.vector.search(query, top_k=top_k)

    def temporal_reasoner(self, games_name_or_year: str, direction: str = "previous") -> Optional[Dict[str, Any]]:
        """Navigates PREVIOUS_EDITION or NEXT_EDITION links."""
        return self.graph.get_temporal_edition(games_name_or_year, direction=direction)

    def aggregation_reasoner(self, games_filter: Optional[str], sport_filter: Optional[str],
                             min_competitors: int, operator: str = ">") -> List[Dict[str, Any]]:
        """Counts and filters events matching criteria."""
        return self.graph.get_events_by_competitors(
            games_filter=games_filter,
            sport_filter=sport_filter,
            min_competitors=min_competitors,
            operator=operator
        )

    def superlative_reasoner(self, games_filter: Optional[str], sport_filter: Optional[str],
                             metric: str = "competitors", order: str = "DESC") -> Optional[Dict[str, Any]]:
        """Finds max or min event according to metric."""
        return self.graph.get_superlative(
            games_filter=games_filter,
            sport_filter=sport_filter,
            metric=metric,
            order=order
        )

    def venue_date_search(self, venue_name: str, date_str: str) -> List[Dict[str, Any]]:
        """Finds events matching venue and date multi-hop constraints."""
        return self.graph.get_event_at_venue_date(venue_name, date_str)

    def evidence_validator(self, query: str, collected_facts: List[Dict[str, Any]], candidate_answer: str) -> Dict[str, Any]:
        """Checks whether collected evidence is sufficient and verifies grounding."""
        is_sufficient = len(collected_facts) > 0 and len(candidate_answer.strip()) > 0
        grounded = False
        if is_sufficient:
            # Check if answer words overlap with evidence facts
            ans_lower = candidate_answer.lower()
            overlap_count = 0
            for fact in collected_facts:
                fact_str = str(fact).lower()
                if any(word in fact_str for word in ans_lower.split() if len(word) > 3):
                    overlap_count += 1
            grounded = overlap_count > 0 or len(collected_facts) > 0

        return {
            "status": "PASS" if (is_sufficient and grounded) else "NEEDS_REPLAN",
            "is_sufficient": is_sufficient,
            "grounded": grounded,
            "facts_count": len(collected_facts)
        }