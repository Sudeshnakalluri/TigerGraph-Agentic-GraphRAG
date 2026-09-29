import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config.settings import API_HOST, API_PORT, EVAL_RESULTS_FILE, PROJECT_ROOT
from backend.graph.graph_service import GraphService
from backend.retrieval.vector_store import VectorStore
from backend.agents.router import QueryComplexityRouter
from backend.pipelines.comparator import PipelineComparator
from backend.evaluation.benchmark_runner import BenchmarkRunner

FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(
    title="TigerGraph Agentic GraphRAG API",
    description="Autonomous Agentic GraphRAG vs GraphRAG vs RAG 3-way comparative benchmark on Olympic Knowledge Graph.",
    version="1.0.0-hackathon"
)

# CORS for frontend (Next.js / React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and Web Dashboard
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_index():
    """Serves the interactive Metrics Dashboard."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "title": "TigerGraph Agentic GraphRAG API",
        "status": "online",
        "dashboard": "Frontend build is in progress. Check /api/status or /docs."
    }

@app.get("/architecture_diagram.svg")
def serve_arch_svg():
    f = FRONTEND_DIR / "architecture_diagram.svg"
    if f.exists():
        return FileResponse(str(f), media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="Diagram not found")

@app.get("/architecture_diagram.html")
def serve_arch_html():
    f = FRONTEND_DIR / "architecture_diagram.html"
    if f.exists():
        return FileResponse(str(f), media_type="text/html")
    raise HTTPException(status_code=404, detail="Page not found")


# Global services
graph_service = GraphService()
vector_store = VectorStore()
router = QueryComplexityRouter()
comparator = PipelineComparator()
benchmark_runner = BenchmarkRunner()

# Request Models
class QueryRequest(BaseModel):
    query: str
    pipeline: Optional[str] = "agentic" # "rag", "graphrag", "agentic"

class CompareRequest(BaseModel):
    query: str
    expected_answer: Optional[str] = None

class RouteRequest(BaseModel):
    query: str

class BenchmarkRequest(BaseModel):
    sample_limit: Optional[int] = 100

@app.get("/health")
@app.get("/api/status")
def get_status():
    """Returns system status, active graph backend, and graph statistics."""
    graph_stat = graph_service.get_status()
    return {
        "status": "online",
        "graph_backend": graph_stat["backend"],
        "is_tigergraph_primary": graph_stat["is_tigergraph_primary"],
        "tigergraph_host": graph_stat["tigergraph_host"],
        "graph_nodes": graph_stat["graph_nodes"],
        "graph_edges": graph_stat["graph_edges"],
        "queries_executed": graph_stat["queries_executed"],
        "entity_breakdown": graph_stat["entity_breakdown"],
        "vector_index_ready": vector_store.index is not None or Path(vector_store.model_name).exists()
    }

@app.post("/api/route")
def route_query(payload: RouteRequest):
    """Classifies query complexity and decides whether agentic reasoning is required."""
    q = payload.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return router.route(q)

@app.post("/api/query")
def run_query(payload: QueryRequest):
    """Executes a single pipeline (rag, graphrag, or agentic)."""
    q = payload.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    p = payload.pipeline.lower()
    if p == "rag":
        return comparator.rag.run(q)
    elif p == "graphrag":
        return comparator.graphrag.run(q)
    else:
        return comparator.agentic.run(q)

@app.post("/api/compare")
def compare_pipelines(payload: CompareRequest):
    """Runs all three pipelines side-by-side and returns answers, trace, and overhead."""
    q = payload.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return comparator.compare(q, expected_answer=payload.expected_answer)

@app.get("/api/graph/subgraph")
def get_subgraph(query: Optional[str] = None, entity_id: Optional[str] = None):
    """Returns nodes and edges for interactive frontend graph visualization."""
    nodes = []
    links = []
    seen_nodes = set()

    target_id = entity_id
    if not target_id and query:
        matches = graph_service.find_entities(query)
        if matches:
            target_id = matches[0]["id"]

    if target_id and target_id in graph_service.local_kg.entities:
        center = graph_service.local_kg.entities[target_id]
        nodes.append({"id": target_id, "name": center.get("name", target_id), "type": center.get("type", "Entity")})
        seen_nodes.add(target_id)

        # 1-hop and 2-hop
        for edge in graph_service.local_kg.get_1hop(target_id):
            nbr = edge["node"]
            nid = nbr["id"]
            if nid not in seen_nodes:
                seen_nodes.add(nid)
                nodes.append({"id": nid, "name": nbr.get("name", nid), "type": nbr.get("type", "Entity")})
            links.append({
                "source": target_id if edge["direction"] == "out" else nid,
                "target": nid if edge["direction"] == "out" else target_id,
                "relation": edge["relation"]
            })
    else:
        # Return sample subgraph of OlympicGames and Sports
        for eid in graph_service.local_kg.type_index.get("OlympicGames", [])[:8]:
            g = graph_service.local_kg.entities[eid]
            nodes.append({"id": eid, "name": g.get("name"), "type": "OlympicGames"})
            seen_nodes.add(eid)
            # Add previous edition edges
            for edge in graph_service.local_kg.get_1hop(eid, relation_type="PREVIOUS_EDITION"):
                if edge["direction"] == "out":
                    prev_id = edge["node"]["id"]
                    if prev_id in seen_nodes:
                        links.append({"source": eid, "target": prev_id, "relation": "PREVIOUS_EDITION"})

    return {"nodes": nodes, "links": links}

@app.get("/api/benchmark/summary")
def get_benchmark_summary():
    """Returns stored benchmark evaluation results."""
    import json
    if EVAL_RESULTS_FILE.exists():
        with open(EVAL_RESULTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # If not yet executed, return empty scaffold
    return {
        "status": "pending",
        "message": "Benchmark has not been run yet. Run POST /api/benchmark/run to execute."
    }

@app.post("/api/benchmark/run")
def trigger_benchmark(payload: BenchmarkRequest):
    """Executes the public benchmark runner across the evaluation dataset."""
    results = benchmark_runner.run_public_benchmark(sample_limit=payload.sample_limit)
    benchmark_runner.generate_hidden_submission()
    return {
        "status": "completed",
        "total_evaluated": results["total_questions_evaluated"],
        "overall_agent_necessity_rate": results["overall_agent_necessity_rate"],
        "roi_analysis": results["roi_analysis"],
        "summary_by_type": results["summary_by_type"]
    }

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    def _open_browser():
        time.sleep(1.0)
        try:
            webbrowser.open(f"http://localhost:{API_PORT}")
        except Exception:
            pass

    threading.Thread(target=_open_browser, daemon=True).start()
    print("=" * 60)
    print(f"🐯 TigerGraph Agentic GraphRAG Server is ONLINE!")
    print(f"👉 Opening Dashboard in your browser: http://localhost:{API_PORT}")
    print(f"👉 Backend API Docs: http://localhost:{API_PORT}/docs")
    print("Keep this terminal window open. Press CTRL+C to stop.")
    print("=" * 60)
    uvicorn.run(app, host=API_HOST, port=API_PORT)