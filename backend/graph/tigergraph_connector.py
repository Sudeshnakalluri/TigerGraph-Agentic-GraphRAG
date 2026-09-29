"""TigerGraph Connector for TigerGraph Savanna Cloud and Local TigerGraph."""
from typing import Dict, List, Any, Optional
import os
import requests
from config.settings import (
    TIGERGRAPH_HOST,
    TIGERGRAPH_USERNAME,
    TIGERGRAPH_PASSWORD,
    TIGERGRAPH_GRAPH,
    TIGERGRAPH_SECRET,
    TIGERGRAPH_TOKEN,
    USE_TIGERGRAPH
)

class TigerGraphConnector:
    """Manages connection and query execution against TigerGraph REST++ & pyTigerGraph."""

    def __init__(self):
        self.host = TIGERGRAPH_HOST.rstrip('/')
        self.username = TIGERGRAPH_USERNAME
        self.password = TIGERGRAPH_PASSWORD
        self.graph_name = TIGERGRAPH_GRAPH
        self.secret = TIGERGRAPH_SECRET
        self.token = TIGERGRAPH_TOKEN
        self.enabled = USE_TIGERGRAPH
        self.conn = None
        self.is_connected = False
        self.queries_count = 0
        self._init_connection()

    def _init_connection(self):
        if not self.enabled:
            self.is_connected = False
            return
        try:
            import pyTigerGraph as tg
            self.conn = tg.TigerGraphConnection(
                host=self.host,
                username=self.username,
                password=self.password,
                graphname=self.graph_name
            )
            # Test ping / echo endpoint
            ping = self.conn.ping()
            if ping or self.conn.echo():
                self.is_connected = True
        except Exception:
            self.is_connected = False

    def get_status(self) -> Dict[str, Any]:
        """Returns connection status and metrics."""
        return {
            "connected": self.is_connected,
            "host": self.host,
            "graph_name": self.graph_name,
            "backend": "TigerGraph" if self.is_connected else "NetworkX (Fallback)",
            "queries_executed": self.queries_count
        }

    def run_gsql_query(self, query_name: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Executes installed GSQL query via pyTigerGraph."""
        if not self.is_connected or not self.conn:
            return None
        try:
            self.queries_count += 1
            return self.conn.runInstalledQuery(query_name, params=params or {})
        except Exception:
            return None