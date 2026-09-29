"""Unit tests for Knowledge Graph and TigerGraph Query Interface."""
import pytest
from backend.graph.graph_service import GraphService

@pytest.fixture
def gs():
    return GraphService()

def test_graph_status(gs):
    status = gs.get_status()
    assert "backend" in status
    assert status["graph_nodes"] > 1000
    assert status["graph_edges"] > 1000

def test_temporal_navigation(gs):
    # Navigate before 2016 Summer Olympics
    prev_games = gs.get_temporal_edition("2016 Summer", direction="previous")
    assert prev_games is not None
    assert "2012" in prev_games.get("name", "")

def test_aggregation_query(gs):
    # Query events with > 73 competitors at 2018 Winter Olympics
    events = gs.get_events_by_competitors(games_filter="2018 Winter", sport_filter="Biathlon", min_competitors=73, operator=">")
    assert len(events) == 5

def test_superlative_query(gs):
    # Event with max competitors in 2008 Athletics
    sup = gs.get_superlative(games_filter="2008 Summer", sport_filter="Athletics", metric="competitors", order="DESC")
    assert sup is not None
    assert "Marathon" in sup["name"] or sup.get("competitors", 0) > 80

def test_venue_date_multihop(gs):
    # Weightlifting on 20 September 1988
    evs = gs.get_event_at_venue_date("Weightlifting", "20 September 1988")
    assert len(evs) > 0
    # Gold winner should be Naim Süleymanoğlu
    gold_edges = gs.get_1hop(evs[0]["id"], relation_type="WON_GOLD")
    assert len(gold_edges) > 0