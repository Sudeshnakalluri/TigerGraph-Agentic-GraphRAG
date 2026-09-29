"""Hybrid Retriever combining dense semantic search with keyword/entity filtering."""
from typing import Dict, List, Any, Optional
from backend.retrieval.vector_store import VectorStore
from backend.graph.graph_service import GraphService

class HybridRetriever:
    """Orchestrates vector and graph evidence retrieval."""

    def __init__(self, vector_store: Optional[VectorStore] = None, graph_service: Optional[GraphService] = None):
        self.vector_store = vector_store or VectorStore()
        self.graph_service = graph_service or GraphService()

    def retrieve(self, query: str, top_k: int = 5, require_graph: bool = False) -> Dict[str, Any]:
        """Retrieves vector chunks and associated graph context."""
        # 1. Vector retrieval
        vector_chunks = self.vector_store.search(query, top_k=top_k)

        # 2. Graph retrieval if requested or query has strong entity matches
        graph_facts = []
        if require_graph:
            # Extract query tokens
            tokens = [t for t in query.split() if len(t) > 3]
            for tok in tokens:
                matches = self.graph_service.find_entities(tok)
                for m in matches[:2]:
                    neighbors = self.graph_service.get_1hop(m["id"])
                    for n in neighbors[:3]:
                        graph_facts.append({
                            "source": m.get("name"),
                            "relation": n["relation"],
                            "target": n["node"].get("name", n["node"].get("id"))
                        })

        return {
            "query": query,
            "vector_chunks": vector_chunks,
            "graph_facts": graph_facts
        }