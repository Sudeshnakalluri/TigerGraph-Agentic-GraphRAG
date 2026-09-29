@echo off
REM =======================================================
REM TigerGraph Agentic GraphRAG Launcher
REM Starts FastAPI Server and opens Metrics Dashboard
REM =======================================================

echo ============================================================
echo Starting TigerGraph Agentic GraphRAG Server...
echo API and Dashboard URL: http://localhost:8000
echo ============================================================

set PYTHONPATH=%CD%
start "" http://localhost:8000
python -m uvicorn backend.api.app:app --host 0.0.0.0 --port 8000
pause
