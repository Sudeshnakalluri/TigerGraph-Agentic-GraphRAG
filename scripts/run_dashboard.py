"""Zero-dependency standalone HTTP server to view the TigerGraph Metrics Dashboard."""
import sys
import os
import webbrowser
import http.server
import socketserver
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

PORT = 3000

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

def main():
    os.chdir(str(FRONTEND_DIR))
    print("=" * 60)
    print(f"TigerGraph Agentic GraphRAG — Standalone Metrics Dashboard")
    print(f"Serving frontend from: {FRONTEND_DIR}")
    print(f"URL: http://localhost:{PORT}")
    print("=" * 60)

    # Open browser
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass

    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print("Server running. Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard server stopped.")

if __name__ == "__main__":
    main()
