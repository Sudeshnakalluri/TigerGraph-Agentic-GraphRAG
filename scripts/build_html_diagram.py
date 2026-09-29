"""Build standalone architecture_diagram.html with inlined SVG and client-side downloaders."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SVG_FILE = PROJECT_ROOT / "docs" / "architecture_diagram.svg"
HTML_FILE = PROJECT_ROOT / "docs" / "architecture_diagram.html"
FRONTEND_SVG = PROJECT_ROOT / "frontend" / "architecture_diagram.svg"
FRONTEND_HTML = PROJECT_ROOT / "frontend" / "architecture_diagram.html"

with open(SVG_FILE, "r", encoding="utf-8") as f:
    svg_content = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TigerGraph Agentic GraphRAG — System Architecture</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #070a12;
      --card-bg: #0f172a;
      --accent-orange: #f05a28;
      --accent-cyan: #06b6d4;
      --accent-purple: #a855f7;
      --accent-emerald: #10b981;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --border-color: rgba(255, 255, 255, 0.1);
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }}
    header {{
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      z-index: 100;
      flex-shrink: 0;
    }}
    .brand-section {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .brand-icon {{
      width: 38px;
      height: 38px;
      background: linear-gradient(135deg, #ff7a45 0%, #f05a28 100%);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 16px;
      color: white;
      box-shadow: 0 0 16px rgba(240, 90, 40, 0.4);
    }}
    .brand-text h1 {{
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(90deg, #ffffff 0%, #fdba74 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .brand-text p {{
      font-size: 0.78rem;
      color: var(--text-muted);
    }}
    .actions-section {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 18px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid transparent;
      text-decoration: none;
      user-select: none;
    }}
    .btn-primary {{
      background: linear-gradient(135deg, #f05a28 0%, #ea580c 100%);
      color: white;
      box-shadow: 0 4px 14px rgba(240, 90, 40, 0.35);
    }}
    .btn-primary:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(240, 90, 40, 0.5);
    }}
    .btn-secondary {{
      background: #1e293b;
      color: #e2e8f0;
      border-color: rgba(255, 255, 255, 0.12);
    }}
    .btn-secondary:hover {{
      background: #27354f;
      color: white;
    }}
    .btn-icon {{
      padding: 9px 14px;
    }}
    .viewer-container {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
      background: radial-gradient(circle at 50% 50%, #101626 0%, #070a12 100%);
      cursor: grab;
    }}
    .viewer-container:active {{
      cursor: grabbing;
    }}
    .diagram-wrapper {{
      transform-origin: center center;
      transition: transform 0.08s ease-out;
      width: 90%;
      max-width: 1400px;
      display: flex;
      justify-content: center;
      align-items: center;
      user-select: none;
    }}
    .diagram-wrapper svg {{
      width: 100%;
      height: auto;
      max-height: 84vh;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      display: block;
    }}
    .status-toast {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: #1e293b;
      color: #e2e8f0;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 500;
      border: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .status-toast.show {{
      transform: translateX(-50%) translateY(0);
    }}
    .hint-bar {{
      position: absolute;
      bottom: 12px;
      right: 18px;
      font-size: 0.75rem;
      color: rgba(255, 255, 255, 0.4);
      pointer-events: none;
    }}
  </style>
</head>
<body>

  <header>
    <div class="brand-section">
      <div class="brand-icon">TG</div>
      <div class="brand-text">
        <h1>TigerGraph Agentic GraphRAG System Architecture</h1>
        <p>Ultra HD Vector Architecture Diagram • 1440 × 960 Viewport</p>
      </div>
    </div>

    <div class="actions-section">
      <button class="btn btn-secondary btn-icon" id="btn-zoom-in" title="Zoom In">➕</button>
      <button class="btn btn-secondary btn-icon" id="btn-zoom-out" title="Zoom Out">➖</button>
      <button class="btn btn-secondary btn-icon" id="btn-reset" title="Reset View">↺ Reset</button>
      
      <button class="btn btn-primary" id="btn-download-svg">
        <span>📥</span> Download SVG (Vector)
      </button>

      <button class="btn btn-secondary" id="btn-download-png">
        <span>🖼️</span> Download PNG (4K / 300 DPI)
      </button>
    </div>
  </header>

  <div class="viewer-container" id="viewer-container">
    <div class="diagram-wrapper" id="diagram-wrapper">
{svg_content}
    </div>
    <div class="hint-bar">💡 Tip: Scroll to zoom, drag to pan</div>
  </div>

  <div class="status-toast" id="status-toast">
    <span id="toast-icon">✓</span>
    <span id="toast-msg">Downloaded successfully!</span>
  </div>

  <canvas id="export-canvas" style="display: none;"></canvas>

  <script>
    let scale = 1.0;
    let translateX = 0;
    let translateY = 0;
    let isDragging = false;
    let startX = 0;
    let startY = 0;

    const wrapper = document.getElementById('diagram-wrapper');
    const container = document.getElementById('viewer-container');
    const toast = document.getElementById('status-toast');
    const toastMsg = document.getElementById('toast-msg');

    function updateTransform() {{
      wrapper.style.transform = `translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
    }}

    function showToast(msg) {{
      toastMsg.innerText = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 3000);
    }}

    // Zoom Controls
    document.getElementById('btn-zoom-in').addEventListener('click', () => {{
      scale = Math.min(scale + 0.15, 3.0);
      updateTransform();
    }});

    document.getElementById('btn-zoom-out').addEventListener('click', () => {{
      scale = Math.max(scale - 0.15, 0.4);
      updateTransform();
    }});

    document.getElementById('btn-reset').addEventListener('click', () => {{
      scale = 1.0;
      translateX = 0;
      translateY = 0;
      updateTransform();
    }});

    // Mouse Wheel Zoom
    container.addEventListener('wheel', (e) => {{
      e.preventDefault();
      const delta = e.deltaY < 0 ? 0.08 : -0.08;
      scale = Math.min(Math.max(scale + delta, 0.4), 3.0);
      updateTransform();
    }}, {{ passive: false }});

    // Drag to Pan
    container.addEventListener('mousedown', (e) => {{
      isDragging = true;
      startX = e.clientX - translateX;
      startY = e.clientY - translateY;
    }});

    window.addEventListener('mousemove', (e) => {{
      if (!isDragging) return;
      translateX = e.clientX - startX;
      translateY = e.clientY - startY;
      updateTransform();
    }});

    window.addEventListener('mouseup', () => {{
      isDragging = false;
    }});

    // 1. Download SVG (Directly from DOM, zero fetch, 100% offline & local file compatible)
    document.getElementById('btn-download-svg').addEventListener('click', () => {{
      try {{
        const svgEl = document.querySelector('#diagram-wrapper svg');
        const svgData = new XMLSerializer().serializeToString(svgEl);
        const blob = new Blob([svgData], {{ type: 'image/svg+xml;charset=utf-8' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tigergraph_agentic_graphrag_architecture.svg';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('Downloaded SVG (Vector) successfully!');
      }} catch (err) {{
        alert('Could not download SVG: ' + err.message);
      }}
    }});

    // 2. Download High-Res PNG (4K 2880 x 1920)
    document.getElementById('btn-download-png').addEventListener('click', () => {{
      showToast('Rendering high-resolution 4K PNG...');
      try {{
        const svgEl = document.querySelector('#diagram-wrapper svg');
        const svgData = new XMLSerializer().serializeToString(svgEl);

        const canvas = document.getElementById('export-canvas');
        const ctx = canvas.getContext('2d');
        
        // 4K Ultra HD Dimensions (2x scale of 1440x960)
        canvas.width = 2880;
        canvas.height = 1920;

        const img = new Image();
        const svgBlob = new Blob([svgData], {{ type: 'image/svg+xml;charset=utf-8' }});
        const url = URL.createObjectURL(svgBlob);

        img.onload = () => {{
          ctx.drawImage(img, 0, 0, 2880, 1920);
          URL.revokeObjectURL(url);

          canvas.toBlob((blob) => {{
            const pngUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = pngUrl;
            a.download = 'tigergraph_agentic_graphrag_architecture_4k.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(pngUrl);
            showToast('Downloaded High-Res PNG (4K) successfully!');
          }}, 'image/png', 1.0);
        }};
        img.src = url;
      }} catch (err) {{
        alert('Could not render PNG: ' + err.message);
      }}
    }});
  </script>
</body>
</html>"""

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(FRONTEND_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(FRONTEND_SVG, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Successfully generated {HTML_FILE} and {FRONTEND_HTML} ({len(html_content)} bytes)")
