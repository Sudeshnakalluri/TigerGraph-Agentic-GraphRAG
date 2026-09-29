"""Knowledge Graph Ingestion & Builder from Olympic Games corpus.jsonl."""
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import CORPUS_FILE, GRAPH_INDEX_FILE
from backend.graph.knowledge_graph import KnowledgeGraph

# Chronological list of Olympic Games editions
SUMMER_GAMES = [
    (1896, "1896 Summer Olympics", "Athens"),
    (1900, "1900 Summer Olympics", "Paris"),
    (1904, "1904 Summer Olympics", "St. Louis"),
    (1908, "1908 Summer Olympics", "London"),
    (1912, "1912 Summer Olympics", "Stockholm"),
    (1920, "1920 Summer Olympics", "Antwerp"),
    (1924, "1924 Summer Olympics", "Paris"),
    (1928, "1928 Summer Olympics", "Amsterdam"),
    (1932, "1932 Summer Olympics", "Los Angeles"),
    (1936, "1936 Summer Olympics", "Berlin"),
    (1948, "1948 Summer Olympics", "London"),
    (1952, "1952 Summer Olympics", "Helsinki"),
    (1956, "1956 Summer Olympics", "Melbourne"),
    (1960, "1960 Summer Olympics", "Rome"),
    (1964, "1964 Summer Olympics", "Tokyo"),
    (1968, "1968 Summer Olympics", "Mexico City"),
    (1972, "1972 Summer Olympics", "Munich"),
    (1976, "1976 Summer Olympics", "Montreal"),
    (1980, "1980 Summer Olympics", "Moscow"),
    (1984, "1984 Summer Olympics", "Los Angeles"),
    (1988, "1988 Summer Olympics", "Seoul"),
    (1992, "1992 Summer Olympics", "Barcelona"),
    (1996, "1996 Summer Olympics", "Atlanta"),
    (2000, "2000 Summer Olympics", "Sydney"),
    (2004, "2004 Summer Olympics", "Athens"),
    (2008, "2008 Summer Olympics", "Beijing"),
    (2012, "2012 Summer Olympics", "London"),
    (2016, "2016 Summer Olympics", "Rio de Janeiro"),
    (2020, "2020 Summer Olympics", "Tokyo"),
    (2024, "2024 Summer Olympics", "Paris"),
]

WINTER_GAMES = [
    (1924, "1924 Winter Olympics", "Chamonix"),
    (1928, "1928 Winter Olympics", "St. Moritz"),
    (1932, "1932 Winter Olympics", "Lake Placid"),
    (1936, "1936 Winter Olympics", "Garmisch-Partenkirchen"),
    (1948, "1948 Winter Olympics", "St. Moritz"),
    (1952, "1952 Winter Olympics", "Oslo"),
    (1956, "1956 Winter Olympics", "Cortina d'Ampezzo"),
    (1960, "1960 Winter Olympics", "Squaw Valley"),
    (1964, "1964 Winter Olympics", "Innsbruck"),
    (1968, "1968 Winter Olympics", "Grenoble"),
    (1972, "1972 Winter Olympics", "Sapporo"),
    (1976, "1976 Winter Olympics", "Innsbruck"),
    (1980, "1980 Winter Olympics", "Lake Placid"),
    (1984, "1984 Winter Olympics", "Sarajevo"),
    (1988, "1988 Winter Olympics", "Calgary"),
    (1992, "1992 Winter Olympics", "Albertville"),
    (1994, "1994 Winter Olympics", "Lillehammer"),
    (1998, "1998 Winter Olympics", "Nagano"),
    (2002, "2002 Winter Olympics", "Salt Lake City"),
    (2006, "2006 Winter Olympics", "Turin"),
    (2010, "2010 Winter Olympics", "Vancouver"),
    (2014, "2014 Winter Olympics", "Sochi"),
    (2018, "2018 Winter Olympics", "Pyeongchang"),
    (2022, "2022 Winter Olympics", "Beijing"),
]

class GraphBuilder:
    """Builds Knowledge Graph by parsing corpus infoboxes and articles."""

    def __init__(self, kg: Optional[KnowledgeGraph] = None):
        self.kg = kg or KnowledgeGraph()

    def build_games_timeline(self):
        """Constructs OlympicGames nodes and PREVIOUS_EDITION/NEXT_EDITION links."""
        # Summer
        for i, (yr, name, city) in enumerate(SUMMER_GAMES):
            gid = f"games_summer_{yr}"
            self.kg.add_entity(gid, "OlympicGames", {
                "name": name,
                "year": yr,
                "season": "Summer",
                "city": city
            })
            if i > 0:
                prev_gid = f"games_summer_{SUMMER_GAMES[i-1][0]}"
                self.kg.add_relation(gid, prev_gid, "PREVIOUS_EDITION")
                self.kg.add_relation(prev_gid, gid, "NEXT_EDITION")

        # Winter
        for i, (yr, name, city) in enumerate(WINTER_GAMES):
            gid = f"games_winter_{yr}"
            self.kg.add_entity(gid, "OlympicGames", {
                "name": name,
                "year": yr,
                "season": "Winter",
                "city": city
            })
            if i > 0:
                prev_gid = f"games_winter_{WINTER_GAMES[i-1][0]}"
                self.kg.add_relation(gid, prev_gid, "PREVIOUS_EDITION")
                self.kg.add_relation(prev_gid, gid, "NEXT_EDITION")

    def parse_infobox(self, text: str) -> Dict[str, str]:
        """Extracts key-value fields from [Infobox ...] section."""
        fields = {}
        if "[Infobox" not in text:
            return fields
        start = text.find("[Infobox")
        end = text.find("\n\n", start)
        if end == -1: end = len(text)
        box_text = text[start:end]
        for line in box_text.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("["):
                parts = line.split(":", 1)
                k = parts[0].strip().lower()
                v = parts[1].strip()
                fields[k] = v
        return fields

    def extract_sport_and_games(self, title: str):
        """Parses 'Sport at the Year Season Olympics – Event' pattern."""
        # Example: 'Canoeing at the 2012 Summer Olympics – Men's K-2 1000 metres'
        pattern = r"^(.*?)\s+at\s+the\s+(\d{4})\s+(Summer|Winter)\s+Olympics\s*[–—-]\s*(.*)$"
        match = re.match(pattern, title, re.IGNORECASE)
        if match:
            sport = match.group(1).strip()
            year = int(match.group(2))
            season = match.group(3).capitalize()
            event_name = match.group(4).strip()
            return sport, year, season, event_name
        return None, None, None, None

    def build_from_corpus(self, limit: Optional[int] = None) -> KnowledgeGraph:
        """Parses corpus.jsonl and builds complete graph."""
        print(f"Building Knowledge Graph from {CORPUS_FILE}...")
        self.build_games_timeline()

        count = 0
        with open(CORPUS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                doc = json.loads(line)
                count += 1
                if limit and count > limit:
                    break

                doc_id = doc.get("doc_id", f"doc_{count}")
                title = doc.get("title", "")
                text = doc.get("text", "")
                url = doc.get("url", "")
                approx_tokens = doc.get("approx_tokens", 0)

                # Add Document Node
                self.kg.add_entity(doc_id, "Document", {
                    "name": title,
                    "title": title,
                    "url": url,
                    "approx_tokens": approx_tokens
                })

                # Parse Title
                sport_name, year, season, event_name = self.extract_sport_and_games(title)
                infobox = self.parse_infobox(text)

                if sport_name and year:
                    # Sport
                    sport_id = f"sport_{sport_name.lower().replace(' ', '_')}"
                    self.kg.add_entity(sport_id, "Sport", {"name": sport_name})

                    # Games
                    games_id = f"games_{season.lower()}_{year}"
                    if games_id not in self.kg.entities:
                        self.kg.add_entity(games_id, "OlympicGames", {
                            "name": f"{year} {season} Olympics",
                            "year": year,
                            "season": season
                        })

                    # Competitors
                    comp_str = infobox.get("competitors", "")
                    comp_match = re.search(r"\d+", comp_str)
                    competitors = int(comp_match.group(0)) if comp_match else 0

                    # Nations
                    nat_str = infobox.get("nations", "")
                    nat_match = re.search(r"\d+", nat_str)
                    nations = int(nat_match.group(0)) if nat_match else 0

                    # Event Node
                    event_id = f"event_{doc_id}"
                    full_event_name = f"{title}"
                    ev_date = infobox.get("date") or infobox.get("dates") or ""
                    venue_name = infobox.get("venue", "")

                    self.kg.add_entity(event_id, "Event", {
                        "name": full_event_name,
                        "short_name": event_name or infobox.get("event", ""),
                        "sport": sport_name,
                        "year": year,
                        "season": season,
                        "competitors": competitors,
                        "nations": nations,
                        "date": ev_date,
                        "venue": venue_name,
                        "doc_id": doc_id
                    })

                    # Relations
                    self.kg.add_relation(event_id, games_id, "PART_OF_GAMES")
                    self.kg.add_relation(event_id, sport_id, "OF_SPORT")
                    self.kg.add_relation(event_id, doc_id, "HAS_DOCUMENT")

                    # Venue
                    if venue_name:
                        venue_id = f"venue_{venue_name.lower().replace(' ', '_')}"
                        self.kg.add_entity(venue_id, "Venue", {"name": venue_name})
                        self.kg.add_relation(event_id, venue_id, "HELD_AT_VENUE")

                    # Athletes & Medals
                    for medal_key, rel_type in [("gold", "WON_GOLD"), ("silver", "WON_SILVER"), ("bronze", "WON_BRONZE")]:
                        ath_str = infobox.get(medal_key, "")
                        if ath_str:
                            # Clean athlete name
                            ath_name = re.sub(r"\([^)]*\)", "", ath_str).strip()
                            # Handle multiple athletes (e.g. pairs, relays)
                            for single_ath in re.split(r"[,\n/]|\s+and\s+", ath_name):
                                single_ath = single_ath.strip()
                                if len(single_ath) > 2 and not single_ath.isdigit():
                                    ath_id = f"athlete_{single_ath.lower().replace(' ', '_')}"
                                    noc = infobox.get(f"{medal_key}noc", "")
                                    self.kg.add_entity(ath_id, "Athlete", {
                                        "name": single_ath,
                                        "country": noc
                                    })
                                    self.kg.add_relation(ath_id, event_id, rel_type)

        print(f"Ingested {count} documents.")
        stats = self.kg.get_stats()
        print(f"Graph Stats: {stats['node_count']} nodes, {stats['edge_count']} edges.")
        print(f"Types: {stats['types']}")

        # Save to JSON
        GRAPH_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.kg.save_to_json(GRAPH_INDEX_FILE)
        print(f"Saved graph index to {GRAPH_INDEX_FILE}")
        return self.kg

if __name__ == "__main__":
    builder = GraphBuilder()
    builder.build_from_corpus()