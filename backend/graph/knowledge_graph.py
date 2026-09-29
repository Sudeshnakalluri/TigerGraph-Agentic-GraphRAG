"""In-memory & persistent NetworkX Knowledge Graph for Olympic Games."""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import networkx as nx

class KnowledgeGraph:
    """High-performance local graph engine with TigerGraph-equivalent query interface."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.type_index: Dict[str, List[str]] = {
            "OlympicGames": [],
            "Sport": [],
            "Event": [],
            "Athlete": [],
            "Venue": [],
            "Nation": [],
            "Document": []
        }

    def add_entity(self, entity_id: str, entity_type: str, properties: Dict[str, Any]):
        """Adds or updates a vertex in the graph."""
        self.entities[entity_id] = {
            "id": entity_id,
            "type": entity_type,
            **properties
        }
        clean_props = {k: v for k, v in properties.items() if k != "type"}
        self.graph.add_node(entity_id, type=entity_type, **clean_props)
        if entity_type in self.type_index and entity_id not in self.type_index[entity_type]:
            self.type_index[entity_type].append(entity_id)

    def add_relation(self, from_id: str, to_id: str, relation_type: str, properties: Optional[Dict[str, Any]] = None):
        """Adds a directed relation between two vertices."""
        props = properties or {}
        self.graph.add_edge(from_id, to_id, key=relation_type, relation=relation_type, **props)

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves entity by ID."""
        return self.entities.get(entity_id)

    def find_entities_by_name(self, name_query: str, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Finds entities matching name substring (case-insensitive)."""
        query = name_query.lower().strip()
        matches = []
        candidates = self.type_index.get(entity_type, list(self.entities.keys())) if entity_type else list(self.entities.keys())
        for eid in candidates:
            ent = self.entities[eid]
            name = ent.get("name", "").lower()
            if query == name or (query in name and len(query) > 2):
                matches.append(ent)
        return matches

    def get_1hop_neighbors(self, entity_id: str, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves direct 1-hop connected neighbors (inward & outward)."""
        if entity_id not in self.graph:
            return []
        neighbors = []
        # Outward edges
        for _, to_node, key, data in self.graph.out_edges(entity_id, keys=True, data=True):
            rel = data.get("relation", key)
            if relation_type and rel != relation_type:
                continue
            target_ent = self.entities.get(to_node, {"id": to_node})
            neighbors.append({
                "direction": "out",
                "relation": rel,
                "node": target_ent
            })
        # Inward edges
        for from_node, _, key, data in self.graph.in_edges(entity_id, keys=True, data=True):
            rel = data.get("relation", key)
            if relation_type and rel != relation_type:
                continue
            source_ent = self.entities.get(from_node, {"id": from_node})
            neighbors.append({
                "direction": "in",
                "relation": rel,
                "node": source_ent
            })
        return neighbors

    def get_2hop_neighbors(self, entity_id: str) -> List[Dict[str, Any]]:
        """Retrieves 2-hop neighborhood expansion with paths."""
        hop1 = self.get_1hop_neighbors(entity_id)
        results = []
        seen_nodes = {entity_id}
        for edge1 in hop1:
            n1 = edge1["node"]
            n1_id = n1["id"]
            results.append({
                "hop": 1,
                "path": [(entity_id, edge1["relation"], n1_id)],
                "target": n1
            })
            seen_nodes.add(n1_id)
            for edge2 in self.get_1hop_neighbors(n1_id):
                n2 = edge2["node"]
                n2_id = n2["id"]
                if n2_id not in seen_nodes:
                    results.append({
                        "hop": 2,
                        "path": [(entity_id, edge1["relation"], n1_id), (n1_id, edge2["relation"], n2_id)],
                        "target": n2
                    })
                    seen_nodes.add(n2_id)
        return results

    def get_temporal_neighbor(self, games_name_or_year: str, direction: str = "previous") -> Optional[Dict[str, Any]]:
        """Navigates PREVIOUS_EDITION or NEXT_EDITION relations for OlympicGames."""
        # Locate games node
        query = games_name_or_year.lower()
        target_games = None
        for eid in self.type_index.get("OlympicGames", []):
            g = self.entities[eid]
            if query in g.get("name", "").lower() or str(g.get("year", "")) in query:
                target_games = g
                break
        if not target_games:
            return None

        rel_key = "PREVIOUS_EDITION" if direction.lower() == "previous" else "NEXT_EDITION"
        gid = target_games["id"]
        for edge in self.get_1hop_neighbors(gid, relation_type=rel_key):
            if edge["direction"] == "out":
                return edge["node"]
        return None

    def get_events_by_competitors(self, games_filter: Optional[str] = None, sport_filter: Optional[str] = None,
                                  min_competitors: int = 0, operator: str = ">") -> List[Dict[str, Any]]:
        """Aggregation query: Finds events matching competitor threshold."""
        matches = []
        for eid in self.type_index.get("Event", []):
            ev = self.entities[eid]
            comp = ev.get("competitors", 0) or 0
            if operator == ">" and comp <= min_competitors:
                continue
            if operator == ">=" and comp < min_competitors:
                continue
            if operator == "<" and comp >= min_competitors:
                continue
            
            # Check games filter
            if games_filter:
                games_match = False
                for edge in self.get_1hop_neighbors(eid, relation_type="PART_OF_GAMES"):
                    if games_filter.lower() in edge["node"].get("name", "").lower():
                        games_match = True
                        break
                if not games_match:
                    continue

            # Check sport filter
            if sport_filter:
                ev_sport = ev.get("sport", "").lower()
                if sport_filter.lower() not in ev_sport:
                    continue

            matches.append(ev)
        return matches

    def get_superlative_event(self, games_filter: Optional[str] = None, sport_filter: Optional[str] = None,
                              metric: str = "competitors", order: str = "DESC") -> Optional[Dict[str, Any]]:
        """Superlative query: Finds event with max/min metric."""
        events = self.get_events_by_competitors(games_filter=games_filter, sport_filter=sport_filter, min_competitors=-1, operator=">")
        if not events:
            return None
        events.sort(key=lambda x: x.get(metric, 0) or 0, reverse=(order.upper() == "DESC"))
        return events[0]

    def get_event_by_venue_and_date(self, venue_query: str, date_query: str) -> List[Dict[str, Any]]:
        """Multi-hop query: Finds events held at a specific venue on/near a date."""
        v_query = venue_query.lower()
        d_query = date_query.lower()
        matching_events = []
        for eid in self.type_index.get("Event", []):
            ev = self.entities[eid]
            # check venue link
            venue_matched = False
            for edge in self.get_1hop_neighbors(eid, relation_type="HELD_AT_VENUE"):
                if v_query in edge["node"].get("name", "").lower():
                    venue_matched = True
                    break
            if not venue_matched:
                continue
            # check date
            ev_date = ev.get("date", "").lower()
            if d_query in ev_date or any(tok in ev_date for tok in d_query.split() if len(tok) > 3):
                matching_events.append(ev)
        return matching_events

    def get_stats(self) -> Dict[str, Any]:
        """Returns vertex and edge counts."""
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "types": {k: len(v) for k, v in self.type_index.items()}
        }

    def save_to_json(self, file_path: Path):
        """Serializes graph to JSON for fast caching."""
        data = {
            "entities": self.entities,
            "edges": [
                {
                    "from": u,
                    "to": v,
                    "relation": d.get("relation", k),
                    "props": {pk: pv for pk, pv in d.items() if pk != "relation"}
                }
                for u, v, k, d in self.graph.edges(keys=True, data=True)
            ]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def load_from_json(self, file_path: Path) -> bool:
        """Loads serialized graph from JSON."""
        if not file_path.exists():
            return False
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.graph.clear()
        self.entities.clear()
        for k in self.type_index:
            self.type_index[k] = []

        for eid, props in data.get("entities", {}).items():
            etype = props.get("type", "Unknown")
            self.add_entity(eid, etype, props)

        for edge in data.get("edges", []):
            self.add_relation(edge["from"], edge["to"], edge["relation"], edge.get("props"))
        return True