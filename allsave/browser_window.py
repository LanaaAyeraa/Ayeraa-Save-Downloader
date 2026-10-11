"""Ayeraa Browser Navigator — High-performance Chromium Subprocess Browser.

Uses Microsoft Edge WebView2 (Chromium engine) for 100% full compatibility
with YouTube (4K/60fps), TikTok, Instagram, Twitter/X, and social media platforms,
featuring an isolated floating HUD for instant 1-click link grabbing.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import threading
import time
import urllib.parse
import urllib.request
from typing import Optional

try:
    import webview
except ImportError:
    webview = None  # Handled gracefully if not installed

logger = logging.getLogger("allsave.browser")


def get_start_page_html(ipc_port: int) -> str:
    """Returns the dark-themed modern Start Page for the Ayeraa Browser Navigator."""
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ayeraa Browser Navigator</title>
  <style>
    :root {{
      --bg: #090D16;
      --card: #111827;
      --card-hover: #1E293B;
      --border: rgba(255, 255, 255, 0.08);
      --border-glow: rgba(124, 58, 237, 0.4);
      --text: #F8FAFC;
      --muted: #94A3B8;
      --accent: #7C3AED;
      --accent-hover: #6D28D9;
      --accent-grad: linear-gradient(135deg, #7C3AED, #4F46E5);
      --success: #10B981;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    body {{
      background: radial-gradient(circle at 50% 0%, #1e1138 0%, var(--bg) 70%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
      user-select: none;
    }}
    .container {{
      width: 100%;
      max-width: 880px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 32px;
    }}
    .header {{
      text-align: center;
      margin-top: 10px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 9999px;
      background: rgba(124, 58, 237, 0.15);
      border: 1px solid var(--border-glow);
      color: #C4B5FD;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 16px;
    }}
    h1 {{
      font-size: 38px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 8px;
      background: linear-gradient(135deg, #FFFFFF 30%, #C4B5FD 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    p.sub {{
      font-size: 15px;
      color: var(--muted);
      max-width: 580px;
      line-height: 1.5;
    }}
    .search-card {{
      width: 100%;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 10px 14px;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
      transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .search-card:focus-within {{
      border-color: var(--accent);
      box-shadow: 0 0 25px rgba(124, 58, 237, 0.35);
    }}
    .search-icon {{
      font-size: 20px;
      color: var(--muted);
      margin-left: 6px;
    }}
    input.search-input {{
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      font-size: 16px;
      color: var(--text);
    }}
    input.search-input::placeholder {{
      color: #64748B;
    }}
    button.btn-go {{
      background: var(--accent-grad);
      color: white;
      border: none;
      border-radius: 12px;
      padding: 12px 24px;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: opacity 0.2s, transform 0.1s;
    }}
    button.btn-go:hover {{
      opacity: 0.92;
      transform: translateY(-1px);
    }}
    .section-title {{
      align-self: flex-start;
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #64748B;
      margin-bottom: -16px;
    }}
    .grid {{
      width: 100%;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 16px;
    }}
    .card-item {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px 14px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text);
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .card-item:hover {{
      background: var(--card-hover);
      border-color: var(--border-glow);
      transform: translateY(-3px);
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
    }}
    .card-icon {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }}
    .yt {{ background: linear-gradient(135deg, #FF0000, #CC0000); }}
    .tt {{ background: linear-gradient(135deg, #000000, #25F4EE); }}
    .ig {{ background: linear-gradient(135deg, #833AB4, #FD1D1D, #FCB045); }}
    .x  {{ background: linear-gradient(135deg, #000000, #333333); }}
    .fb {{ background: linear-gradient(135deg, #1877F2, #0D65D9); }}
    .gg {{ background: linear-gradient(135deg, #4285F4, #34A853); }}
    .sc {{ background: linear-gradient(135deg, #FF5500, #FF3300); }}
    .pt {{ background: linear-gradient(135deg, #E60023, #B8001B); }}
    .card-name {{
      font-size: 14px;
      font-weight: 600;
    }}
    .tips-box {{
      width: 100%;
      background: rgba(124, 58, 237, 0.08);
      border: 1px dashed rgba(124, 58, 237, 0.35);
      border-radius: 16px;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    .tips-icon {{
      font-size: 28px;
    }}
    .tips-text h4 {{
      font-size: 14px;
      font-weight: 700;
      color: #C4B5FD;
      margin-bottom: 2px;
    }}
    .tips-text p {{
      font-size: 13px;
      color: var(--muted);
      line-height: 1.4;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="badge">🌐 Ayeraa Chromium Navigator</div>
      <h1>Jelajahi Media & Video</h1>
      <p class="sub">Tonton dan jelajahi situs media sosial favorit. Klik tombol <b>Ambil Link</b> kapan saja untuk mengunduh video dengan kualitas terbaik.</p>
    </div>

    <div class="search-card">
      <span class="search-icon">🔍</span>
      <input id="navInput" class="search-input" type="text" placeholder="Ketik URL (misal: youtube.com) atau cari di Google..." autofocus autocomplete="off">
      <button class="btn-go" onclick="doNavigate()">Jelajahi ➔</button>
    </div>

    <div class="section-title">Akses Cepat Platform</div>
    <div class="grid">
      <div class="card-item" onclick="openUrl('https://www.youtube.com')">
        <div class="card-icon yt">▶</div>
        <div class="card-name">YouTube</div>
      </div>
      <div class="card-item" onclick="openUrl('https://www.tiktok.com')">
        <div class="card-icon tt">🎵</div>
        <div class="card-name">TikTok</div>
      </div>
      <div class="card-item" onclick="openUrl('https://www.instagram.com')">
        <div class="card-icon ig">📸</div>
        <div class="card-name">Instagram</div>
      </div>
      <div class="card-item" onclick="openUrl('https://x.com')">
        <div class="card-icon x">𝕏</div>
        <div class="card-name">Twitter / X</div>
      </div>
      <div class="card-item" onclick="openUrl('https://www.facebook.com')">
        <div class="card-icon fb">👥</div>
        <div class="card-name">Facebook</div>
      </div>
      <div class="card-item" onclick="openUrl('https://www.google.com')">
        <div class="card-icon gg">🌐</div>
        <div class="card-name">Google</div>
      </div>
      <div class="card-item" onclick="openUrl('https://soundcloud.com')">
        <div class="card-icon sc">☁</div>
        <div class="card-name">SoundCloud</div>
      </div>
      <div class="card-item" onclick="openUrl('https://www.pinterest.com')">
        <div class="card-icon pt">📌</div>
        <div class="card-name">Pinterest</div>
      </div>
    </div>

    <div class="tips-box">
      <div class="tips-icon">⚡</div>
      <div class="tips-text">
        <h4>Fitur Rahasia Alt+B & Tombol Ambil Link</h4>
        <p>Saat video sedang diputar, tombol floating <b>📥 Ambil Link ke Downloader</b> akan selalu tersedia di pojok atas layar. Link video akan otomatis disalin dan diproses di Ayeraa Save Downloader.</p>
      </div>
    </div>
  </div>

  <script>
    function doNavigate() {{
      const val = document.getElementById('navInput').value.trim();
      if (!val) return;
      if (window.pywebview && window.pywebview.api) {{
        window.pywebview.api.navigate(val);
      }} else {{
        openUrl(val);
      }}
    }}

    function openUrl(url) {{
      if (window.pywebview && window.pywebview.api) {{
        window.pywebview.api.navigate(url);
      }} else {{
        if (!url.startsWith('http://') && !url.startsWith('https://')) {{
          if (url.includes('.') && !url.includes(' ')) {{
            url = 'https://' + url;
          }} else {{
            url = 'https://www.google.com/search?q=' + encodeURIComponent(url);
          }}
        }}
        window.location.href = url;
      }}
    }}

    document.getElementById('navInput').addEventListener('keydown', function(e) {{
      if (e.key === 'Enter') doNavigate();
    }});
  </script>
</body>
</html>"""


def get_injected_hud_js(ipc_port: int) -> str:
    """Returns the JavaScript injected into every browsed page to provide the floating HUD."""
    return f"""(function() {{
  if (window.__ayeraa_hud_injected) return;
  window.__ayeraa_hud_injected = true;

  const IPC_PORT = {ipc_port};

  function createHUD() {{
    if (document.getElementById('ayeraa-hud-host')) return;

    const host = document.createElement('div');
    host.id = 'ayeraa-hud-host';
    host.style.position = 'fixed';
    host.style.top = '12px';
    host.style.right = '16px';
    host.style.zIndex = '2147483647';
    host.style.pointerEvents = 'auto';

    const shadow = host.attachShadow({{ mode: 'open' }});

    shadow.innerHTML = `
      <style>
        * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .bar {{
          display: flex;
          align-items: center;
          gap: 6px;
          background: rgba(15, 23, 42, 0.94);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 9999px;
          padding: 6px 10px;
          box-shadow: 0 10px 25px -5px rgba(0,0,0,0.6), 0 0 15px rgba(124, 58, 237, 0.3);
          color: #F8FAFC;
          font-size: 13px;
          user-select: none;
          transition: all 0.2s ease;
        }}
        .bar:hover {{
          border-color: rgba(124, 58, 237, 0.6);
          box-shadow: 0 12px 30px -5px rgba(0,0,0,0.7), 0 0 20px rgba(124, 58, 237, 0.45);
        }}
        .brand {{
          display: flex;
          align-items: center;
          gap: 4px;
          font-weight: 800;
          font-size: 12px;
          color: #C4B5FD;
          padding: 0 4px;
        }}
        .btn {{
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border: none;
          outline: none;
          cursor: pointer;
          border-radius: 9999px;
          font-size: 12px;
          font-weight: 600;
          color: #F8FAFC;
          transition: transform 0.1s, opacity 0.15s, background 0.2s;
        }}
        .btn:active {{
          transform: scale(0.94);
        }}
        .btn-icon {{
          background: rgba(255, 255, 255, 0.08);
          width: 28px;
          height: 28px;
          border-radius: 50%;
        }}
        .btn-icon:hover {{
          background: rgba(255, 255, 255, 0.18);
        }}
        .btn-grab {{
          background: linear-gradient(135deg, #7C3AED, #4F46E5);
          padding: 6px 14px;
          font-weight: 700;
          gap: 6px;
          box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
        }}
        .btn-grab:hover {{
          filter: brightness(1.1);
        }}
        .btn-grab.success {{
          background: linear-gradient(135deg, #10B981, #059669) !important;
        }}
        .btn-min {{
          background: transparent;
          color: #94A3B8;
          width: 24px;
          height: 24px;
          font-size: 14px;
        }}
        .btn-min:hover {{
          color: #F8FAFC;
        }}
        .min-bubble {{
          display: none;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: linear-gradient(135deg, #7C3AED, #4F46E5);
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 18px;
          box-shadow: 0 4px 16px rgba(124, 58, 237, 0.5);
          border: 1px solid rgba(255,255,255,0.2);
          transition: transform 0.15s;
        }}
        .min-bubble:hover {{
          transform: scale(1.1);
        }}
        .search-modal {{
          display: none;
          position: absolute;
          top: 48px;
          right: 0;
          background: #111827;
          border: 1px solid rgba(124, 58, 237, 0.4);
          border-radius: 12px;
          padding: 8px;
          box-shadow: 0 10px 25px rgba(0,0,0,0.6);
          width: 320px;
          display: flex;
          gap: 6px;
        }}
        .search-modal.hidden {{
          display: none !important;
        }}
        .search-input {{
          flex: 1;
          background: #090D16;
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 8px;
          padding: 6px 10px;
          color: #fff;
          font-size: 12px;
          outline: none;
        }}
        .search-input:focus {{
          border-color: #7C3AED;
        }}
        .toast {{
          position: fixed;
          bottom: 24px;
          right: 24px;
          background: rgba(16, 185, 129, 0.95);
          color: white;
          padding: 10px 18px;
          border-radius: 10px;
          font-weight: 700;
          font-size: 13px;
          box-shadow: 0 8px 20px rgba(0,0,0,0.5);
          opacity: 0;
          pointer-events: none;
          transform: translateY(10px);
          transition: all 0.25s ease;
          z-index: 2147483647;
        }}
        .toast.show {{
          opacity: 1;
          transform: translateY(0);
        }}
      </style>

      <div id="bar" class="bar">
        <span class="brand">⚡ Ayeraa</span>
        <button id="btnBack" class="btn btn-icon" title="Kembali">◀</button>
        <button id="btnFwd" class="btn btn-icon" title="Maju">▶</button>
        <button id="btnReload" class="btn btn-icon" title="Muat Ulang">↻</button>
        <button id="btnHome" class="btn btn-icon" title="Halaman Utama">🏠</button>
        <button id="btnSearch" class="btn btn-icon" title="Ketik URL / Cari">🔍</button>
        <button id="btnGrab" class="btn btn-grab" title="Ambil link video ini ke Ayeraa Save Downloader">
          📥 Ambil Link
        </button>
        <button id="btnMin" class="btn btn-min" title="Sembunyikan HUD">−</button>
      </div>

      <div id="searchModal" class="search-modal hidden">
        <input id="quickInput" class="search-input" placeholder="Ketik URL atau cari... (Enter)">
        <button id="btnQuickGo" class="btn btn-grab" style="padding:6px 12px;">➔</button>
      </div>

      <div id="bubble" class="min-bubble" title="Buka Ayeraa Toolbar">⚡</div>
      <div id="toast" class="toast">✓ Link berhasil dikirim ke Downloader!</div>
    `;

    document.body.appendChild(host);

    const bar = shadow.getElementById('bar');
    const bubble = shadow.getElementById('bubble');
    const toast = shadow.getElementById('toast');
    const btnGrab = shadow.getElementById('btnGrab');
    const searchModal = shadow.getElementById('searchModal');
    const quickInput = shadow.getElementById('quickInput');

    function showToast(msg) {{
      toast.innerText = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2200);
    }}

    btnGrab.addEventListener('click', function() {{
      const currentUrl = window.location.href;
      
      // 1. Send via pywebview API
      if (window.pywebview && window.pywebview.api && window.pywebview.api.grab_url) {{
        window.pywebview.api.grab_url(currentUrl);
      }}

      // 2. Direct fetch to local IPC server
      try {{
        fetch('http://127.0.0.1:' + IPC_PORT + '/grab?url=' + encodeURIComponent(currentUrl), {{
          mode: 'no-cors'
        }}).catch(() => {{}});
      }} catch (err) {{}}

      // 3. System clipboard fallback
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(currentUrl).catch(() => {{}});
      }}

      // Visual feedback
      btnGrab.classList.add('success');
      btnGrab.innerHTML = '✓ Terkirim!';
      showToast('✓ Link berhasil dikirim ke Downloader!');
      setTimeout(() => {{
        btnGrab.classList.remove('success');
        btnGrab.innerHTML = '📥 Ambil Link';
      }}, 2000);
    }});

    shadow.getElementById('btnBack').addEventListener('click', () => history.back());
    shadow.getElementById('btnFwd').addEventListener('click', () => history.forward());
    shadow.getElementById('btnReload').addEventListener('click', () => location.reload());
    shadow.getElementById('btnHome').addEventListener('click', () => {{
      if (window.pywebview && window.pywebview.api && window.pywebview.api.go_home) {{
        window.pywebview.api.go_home();
      }}
    }});

    shadow.getElementById('btnSearch').addEventListener('click', () => {{
      searchModal.classList.toggle('hidden');
      if (!searchModal.classList.contains('hidden')) {{
        quickInput.value = window.location.href;
        quickInput.focus();
        quickInput.select();
      }}
    }});

    function submitQuick() {{
      const q = quickInput.value.trim();
      if (!q) return;
      searchModal.classList.add('hidden');
      if (window.pywebview && window.pywebview.api && window.pywebview.api.navigate) {{
        window.pywebview.api.navigate(q);
      }} else {{
        let target = q;
        if (!target.startsWith('http://') && !target.startsWith('https://')) {{
          if (target.includes('.') && !target.includes(' ')) target = 'https://' + target;
          else target = 'https://www.google.com/search?q=' + encodeURIComponent(target);
        }}
        window.location.href = target;
      }}
    }}

    shadow.getElementById('btnQuickGo').addEventListener('click', submitQuick);
    quickInput.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter') submitQuick();
      if (e.key === 'Escape') searchModal.classList.add('hidden');
    }});

    shadow.getElementById('btnMin').addEventListener('click', () => {{
      bar.style.display = 'none';
      searchModal.classList.add('hidden');
      bubble.style.display = 'flex';
    }});

    bubble.addEventListener('click', () => {{
      bubble.style.display = 'none';
      bar.style.display = 'flex';
    }});
  }}

  if (document.body) {{
    createHUD();
  }} else {{
    document.addEventListener('DOMContentLoaded', createHUD);
  }}

  // SPA navigation observation
  let lastUrl = window.location.href;
  setInterval(() => {{
    if (window.location.href !== lastUrl) {{
      lastUrl = window.location.href;
      createHUD();
    }}
  }}, 1000);
}})();"""


class BrowserApi:
    """Python API exposed to Edge WebView2 JavaScript runtime."""

    def __init__(self, window: webview.Window, ipc_port: int) -> None:
        self.window = window
        self.ipc_port = ipc_port
        self.start_html = get_start_page_html(ipc_port)

    def grab_url(self, url: str) -> dict[str, str]:
        """Triggered when the user clicks 'Ambil Link ke Downloader'."""
        clean_url = (url or "").strip()
        if not clean_url:
            return {"status": "empty"}

        # Notify local IPC server
        try:
            req_url = f"http://127.0.0.1:{self.ipc_port}/grab?url={urllib.parse.quote(clean_url)}"
            req = urllib.request.Request(req_url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                resp.read()
        except Exception as e:
            logger.debug("IPC grab request failed: %s", e)

        return {"status": "ok", "url": clean_url}

    def navigate(self, query: str) -> dict[str, str]:
        """Navigates the webview to a specific URL or performs a web search."""
        target = (query or "").strip()
        if not target:
            return {"status": "empty"}

        if not target.startswith("http://") and not target.startswith("https://") and not target.startswith("about:"):
            if "." in target and " " not in target:
                target = "https://" + target
            else:
                target = f"https://www.google.com/search?q={urllib.parse.quote(target)}"

        if self.window:
            self.window.load_url(target)
        return {"status": "navigating", "target": target}

    def go_home(self) -> dict[str, str]:
        """Returns to the Ayeraa Start Page."""
        if self.window:
            self.window.load_html(self.start_html)
        return {"status": "ok"}


def _on_window_loaded(window: webview.Window, ipc_port: int) -> None:
    """Injects the floating HUD into any loaded web page."""
    try:
        current_url = window.get_current_url()
        # Do not inject HUD on internal blank/null start pages (start page already has controls)
        if not current_url or current_url.startswith("data:"):
            return

        js = get_injected_hud_js(ipc_port)
        window.evaluate_js(js)
    except Exception as e:
        logger.debug("HUD injection error: %s", e)


def run_browser(ipc_port: int = 48231, initial_url: str = "") -> None:
    """Starts the Ayeraa Browser Navigator process using Microsoft Edge WebView2."""
    if webview is None:
        print("pywebview is not installed.", file=sys.stderr)
        sys.exit(1)

    start_html = get_start_page_html(ipc_port)

    api_holder: list[Optional[BrowserApi]] = [None]

    # Create browser window
    if initial_url and initial_url.startswith("http"):
        window = webview.create_window(
            title="Ayeraa Browser Navigator (Alt+B)",
            url=initial_url,
            width=1120,
            height=740,
            min_size=(600, 480),
        )
    else:
        window = webview.create_window(
            title="Ayeraa Browser Navigator (Alt+B)",
            html=start_html,
            width=1120,
            height=740,
            min_size=(600, 480),
        )

    api = BrowserApi(window, ipc_port)
    api_holder[0] = api
    window.expose(api.grab_url, api.navigate, api.go_home)

    window.events.loaded += lambda: _on_window_loaded(window, ipc_port)

    # Start Edge Chromium WebView2 engine
    webview.start(gui="edgechromium", debug=False)


def run_browser_cli() -> None:
    """CLI handler when invoked with --browser."""
    parser = argparse.ArgumentParser(description="Ayeraa Browser Navigator")
    parser.add_argument("--browser", action="store_true", help="Launch browser subprocess")
    parser.add_argument("--ipc-port", type=int, default=48231, help="Main app IPC HTTP port")
    parser.add_argument("--url", type=str, default="", help="Initial URL to open")
    args, _ = parser.parse_known_args()

    run_browser(ipc_port=args.ipc_port, initial_url=args.url)


if __name__ == "__main__":
    run_browser_cli()
