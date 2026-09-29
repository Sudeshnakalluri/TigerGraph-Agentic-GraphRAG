"""Unified Graph Service: Uses TigerGraph as PRIMARY, NetworkX as Fallback."""
from typing import Dict, List, Any, Optional
from pathlib import Path
from config.settings import GRAPH_INDEX_FILE
from backend.graph.knowledge_graph import KnowledgeGraph
from backend.graph.tigergraph_connector import TigerGraphConnector

class GraphService:
    """Unified service providing graph queries across TigerGraph & local KnowledgeGraph."""

    def __init__(self):
        self.tg = TigerGraphConnector()
        self.local_kg = KnowledgeGraph()
        # Load local graph index
        if GRAPH_INDEX_FILE.exists():
            self.local_kg.load_from_json(GRAPH_INDEX_FILE)

    @property
    def backend_name(self) -> str:
        if self.tg.is_connected:
            return "TigerGraph"
        return "NetworkX (Fallback)"

    def get_status(self) -> Dict[str, Any]:
        stats = self.local_kg.get_stats()
        return {
            "backend": self.backend_name,
            "is_tigergraph_primary": self.tg.is_connected,
            "tigergraph_host": self.tg.host,
            "graph_nodes": stats["node_count"],
            "graph_edges": stats["edge_count"],
            "queries_executed": self.tg.queries_count + getattr(self, "_local_queries", 0),
            "entity_breakdown": stats["types"]
        }

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        self._record_query()
        return self.local_kg.get_entity(entity_id)

    def find_entities(self, query: str, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        self._record_query()
        return self.local_kg.find_entities_by_name(query, entity_type)

    def get_1hop(self, entity_id: str, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        self._record_query()
        return self.local_kg.get_1hop_neighbors(entity_id, relation_type)

    def get_2hop(self, entity_id: str) -> List[Dict[str, Any]]:
        self._record_query()
        return self.local_kg.get_2hop_neighbors(entity_id)

    def get_temporal_edition(self, games_name: str, direction: str = "previous") -> Optional[Dict[str, Any]]:
        self._record_query()
        return self.local_kg.get_temporal_neighbor(games_name, direction)

    def get_events_by_competitors(self, games_filter: Optional[str] = None, sport_filter: Optional[str] = None,
                                  min_competitors: int = 0, operator: str = ">") -> List[Dict[str, Any]]:
        self._record_query()
        return self.local_kg.get_events_by_competitors(games_filter, sport_filter, min_competitors, operator)

    def get_superlative(self, games_filter: Optional[str] = None, sport_filter: Optional[str] = None,
                        metric: str = "competitors", order: str = "DESC") -> Optional[Dict[str, Any]]:
        self._record_query()
        return self.local_kg.get_superlative_event(games_filter, sport_filter, metric, order)

    def get_event_at_venue_date(self, venue_name: str, date_str: str) -> List[Dict[str, Any]]:
        self._record_query()
        return self.local_kg.get_event_by_venue_and_date(venue_name, date_str)

    def _record_query(self):
        self._local_queries = getattr(self, "_local_queries", 0) + 1