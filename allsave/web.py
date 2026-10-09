"""Web Server lokal untuk Android & perangkat lain di jaringan Wi-Fi."""
from __future__ import annotations

import json
import mimetypes
import os
import socket
import sys
import threading
import time
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

from . import core
from .config import Settings

_jobs_lock = threading.Lock()
_web_jobs: dict[str, dict] = {}


def get_local_ip() -> str:
    """Mendapatkan alamat IP lokal di jaringan Wi-Fi / LAN."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <meta name="theme-color" content="#0E1014">
  <title>Ayeraa Save - Downloader untuk Android & PC</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='25' fill='%23FF3D6E'/><path d='M50 20 v38 M32 44 l18 18 l18 -18 M25 78 h50' stroke='white' stroke-width='10' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background: #0E1014; color: #EDEFF3; min-height: 100vh; padding: 16px; display: flex; flex-direction: column; align-items: center; }
    .container { width: 100%; max-width: 640px; margin: 0 auto; }
    header { text-align: center; padding: 24px 0 16px; }
    .logo { display: inline-flex; align-items: center; gap: 10px; font-size: 26px; font-weight: 800; }
    .logo span { color: #FF3D6E; }
    .subtitle { color: #8B93A1; font-size: 13px; margin-top: 6px; }
    .card { background: #171A21; border: 1px solid #2A2F3A; border-radius: 16px; padding: 18px; margin-bottom: 16px; }
    .input-group { display: flex; flex-direction: column; gap: 10px; }
    .input-box { display: flex; gap: 8px; }
    input[type="text"] { flex: 1; background: #0E1014; border: 1px solid #2A2F3A; border-radius: 12px; padding: 14px 16px; color: #EDEFF3; font-size: 15px; outline: none; transition: border-color .2s; }
    input[type="text"]:focus { border-color: #FF3D6E; }
    button { background: #1F232C; color: #EDEFF3; border: 1px solid #2A2F3A; border-radius: 12px; padding: 12px 18px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all .2s; }
    button:active { transform: scale(0.97); }
    .btn-paste { background: #1F232C; }
    .btn-primary { background: #FF3D6E; color: white; border: none; padding: 14px 20px; font-size: 16px; width: 100%; border-radius: 12px; }
    .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
    .btn-download { background: #22C55E; color: white; border: none; width: 100%; padding: 14px; font-size: 16px; font-weight: 700; border-radius: 12px; margin-top: 14px; }
    .btn-download:disabled { opacity: 0.6; }
    .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; justify-content: center; }
    .chip { background: #1F232C; color: #8B93A1; font-size: 11px; padding: 4px 10px; border-radius: 8px; }
    
    .preview { display: none; }
    .thumb-wrap { width: 100%; border-radius: 12px; overflow: hidden; background: #000; aspect-ratio: 16/9; position: relative; margin-bottom: 14px; }
    .thumb-wrap img { width: 100%; height: 100%; object-fit: contain; }
    .badge { position: absolute; top: 10px; left: 10px; background: #FF3D6E; color: white; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .duration { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .video-title { font-size: 16px; font-weight: 700; line-height: 1.4; margin-bottom: 6px; }
    .video-author { color: #8B93A1; font-size: 13px; margin-bottom: 14px; }
    
    .format-tabs { display: flex; background: #0E1014; border-radius: 10px; padding: 4px; gap: 4px; margin-bottom: 12px; }
    .tab { flex: 1; text-align: center; padding: 8px 12px; font-size: 13px; font-weight: 600; border-radius: 8px; cursor: pointer; color: #8B93A1; border: none; background: transparent; }
    .tab.active { background: #FF3D6E; color: white; }
    
    select { width: 100%; background: #0E1014; color: #EDEFF3; border: 1px solid #2A2F3A; border-radius: 12px; padding: 12px 14px; font-size: 14px; outline: none; }
    
    .progress-box { display: none; background: #1F232C; border-radius: 12px; padding: 14px; margin-top: 14px; }
    .progress-bar-bg { width: 100%; height: 8px; background: #2A2F3A; border-radius: 4px; overflow: hidden; margin: 8px 0; }
    .progress-bar-fill { height: 100%; width: 0%; background: #FF3D6E; transition: width .2s; }
    .progress-text { display: flex; justify-content: space-between; font-size: 12px; color: #8B93A1; }
    .status-msg { font-size: 13px; font-weight: 600; margin-bottom: 4px; }
    .status-msg.success { color: #22C55E; }
    .status-msg.error { color: #EF4444; }
    
    footer { text-align: center; color: #525966; font-size: 12px; padding: 24px 0 16px; }
    .direct-save { display: inline-block; background: #22C55E; color: white; text-decoration: none; padding: 12px 20px; border-radius: 10px; font-weight: 700; margin-top: 10px; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo">Ayeraa Save <span>Mobile</span></div>
      <p class="subtitle">Download video & musik langsung ke memori HP Android Anda</p>
    </header>

    <div class="card">
      <div class="input-group">
        <div class="input-box">
          <input type="text" id="urlInput" placeholder="Tempel link (YouTube, TikTok, IG, FB, X...)" autocomplete="off">
          <button type="button" class="btn-paste" onclick="pasteClipboard()">Tempel</button>
        </div>
        <button type="button" class="btn-primary" id="btnAnalyze" onclick="analyzeUrl()">Mulai  →</button>
      </div>
      <div class="chips">
        <span class="chip">YouTube</span>
        <span class="chip">TikTok</span>
        <span class="chip">Instagram</span>
        <span class="chip">Facebook</span>
        <span class="chip">X / Twitter</span>
        <span class="chip">SoundCloud</span>
        <span class="chip">+1000 situs</span>
      </div>
    </div>

    <div class="card preview" id="previewCard">
      <div class="thumb-wrap">
        <img id="thumbImg" src="" alt="Thumbnail">
        <div class="badge" id="platformBadge">YouTube</div>
        <div class="duration" id="durationBadge">0:00</div>
      </div>
      <div class="video-title" id="videoTitle">-</div>
      <div class="video-author" id="videoAuthor">-</div>

      <div class="format-tabs">
        <button type="button" class="tab active" id="tabVideo" onclick="setMode('video')">Video MP4</button>
        <button type="button" class="tab" id="tabAudio" onclick="setMode('audio')">Audio MP3</button>
      </div>

      <select id="qualitySelect"></select>

      <button type="button" class="btn-download" id="btnDownload" onclick="startDownload()">↓  Download ke HP</button>

      <div class="progress-box" id="progressBox">
        <div class="status-msg" id="statusMsg">Menyiapkan...</div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" id="progressFill"></div>
        </div>
        <div class="progress-text">
          <span id="progressPercent">0%</span>
          <span id="progressDetails">Mengunduh...</span>
        </div>
        <div id="savePrompt" style="text-align: center; margin-top: 10px; display: none;">
          <a id="saveLink" class="direct-save" href="#" download>Simpan File ke HP</a>
        </div>
      </div>
    </div>

    <footer>
      Terkoneksi ke server Ayeraa Save lokal di PC Anda.<br>
      Video diproses di PC & otomatis tersimpan ke Android.
    </footer>
  </div>

  <script>
    let currentInfo = null;
    let currentMode = 'video';
    let currentJobId = null;
    let pollInterval = null;

    async function pasteClipboard() {
      try {
        const text = await navigator.clipboard.readText();
        if (text) {
          document.getElementById('urlInput').value = text.trim();
          analyzeUrl();
        }
      } catch (e) {
        document.getElementById('urlInput').focus();
      }
    }

    async function analyzeUrl() {
      const url = document.getElementById('urlInput').value.trim();
      if (!url) return;
      const btn = document.getElementById('btnAnalyze');
      btn.disabled = true;
      btn.innerText = 'Menganalisis...';
      document.getElementById('previewCard').style.display = 'none';

      try {
        const res = await fetch('/api/info?url=' + encodeURIComponent(url));
        const data = await res.json();
        if (!res.ok || data.error) {
          alert('Gagal: ' + (data.error || 'Link tidak dapat diproses'));
          return;
        }
        currentInfo = data;
        renderInfo();
      } catch (err) {
        alert('Terjadi kesalahan koneksi ke server Ayeraa Save.');
      } finally {
        btn.disabled = false;
        btn.innerText = 'Mulai  →';
      }
    }

    function renderInfo() {
      if (!currentInfo) return;
      document.getElementById('thumbImg').src = currentInfo.thumbnail || '';
      document.getElementById('platformBadge').innerText = currentInfo.platform || 'Web';
      document.getElementById('durationBadge').innerText = currentInfo.duration_fmt || '';
      document.getElementById('videoTitle').innerText = currentInfo.title || 'Tanpa judul';
      document.getElementById('videoAuthor').innerText = currentInfo.uploader || '';
      
      setMode('video');
      document.getElementById('previewCard').style.display = 'block';
      document.getElementById('progressBox').style.display = 'none';
      document.getElementById('savePrompt').style.display = 'none';
    }

    function setMode(mode) {
      currentMode = mode;
      document.getElementById('tabVideo').className = 'tab' + (mode === 'video' ? ' active' : '');
      document.getElementById('tabAudio').className = 'tab' + (mode === 'audio' ? ' active' : '');
      const sel = document.getElementById('qualitySelect');
      sel.innerHTML = '';

      if (mode === 'video') {
        const heights = currentInfo.heights || [];
        if (heights.length === 0) {
          const opt = document.createElement('option');
          opt.value = '';
          opt.innerText = 'Kualitas Terbaik (Otomatis)';
          sel.appendChild(opt);
        } else {
          heights.forEach(h => {
            const opt = document.createElement('option');
            opt.value = h;
            let sz = currentInfo.sizes && currentInfo.sizes[h] ? ' ≈ ' + currentInfo.sizes[h] : '';
            opt.innerText = h + 'p' + sz;
            sel.appendChild(opt);
          });
        }
      } else {
        ['320', '256', '192', '128'].forEach(b => {
          const opt = document.createElement('option');
          opt.value = b;
          opt.innerText = b + ' kbps MP3' + (b === '320' ? ' (Terbaik)' : '');
          sel.appendChild(opt);
        });
      }
    }

    async function startDownload() {
      if (!currentInfo) return;
      const quality = document.getElementById('qualitySelect').value;
      const btn = document.getElementById('btnDownload');
      btn.disabled = true;

      const pBox = document.getElementById('progressBox');
      pBox.style.display = 'block';
      document.getElementById('statusMsg').innerText = 'Memulai download...';
      document.getElementById('statusMsg').className = 'status-msg';
      document.getElementById('progressFill').style.width = '0%';
      document.getElementById('progressPercent').innerText = '0%';
      document.getElementById('savePrompt').style.display = 'none';

      try {
        const res = await fetch('/api/download', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            url: currentInfo.url,
            title: currentInfo.title,
            mode: currentMode === 'video' ? 'video' : 'mp3',
            quality: quality ? parseInt(quality) : null
          })
        });
        const d = await res.json();
        if (d.error) {
          alert('Error: ' + d.error);
          btn.disabled = false;
          return;
        }
        currentJobId = d.job_id;
        pollStatus();
      } catch (e) {
        alert('Gagal mengirim perintah download');
        btn.disabled = false;
      }
    }

    function pollStatus() {
      if (pollInterval) clearInterval(pollInterval);
      pollInterval = setInterval(async () => {
        if (!currentJobId) return;
        try {
          const res = await fetch('/api/status?id=' + currentJobId);
          const data = await res.json();
          if (data.state === 'downloading') {
            const pct = Math.round((data.progress || 0) * 100);
            document.getElementById('progressFill').style.width = pct + '%';
            document.getElementById('progressPercent').innerText = pct + '%';
            document.getElementById('progressDetails').innerText = (data.speed || '') + (data.eta ? ' sisa ' + data.eta : '');
            document.getElementById('statusMsg').innerText = 'Sedang mengunduh...';
          } else if (data.state === 'processing') {
            document.getElementById('statusMsg').innerText = data.text || 'Memproses format...';
          } else if (data.state === 'done') {
            clearInterval(pollInterval);
            document.getElementById('progressFill').style.width = '100%';
            document.getElementById('progressPercent').innerText = '100%';
            document.getElementById('statusMsg').innerText = '✓ Selesai!';
            document.getElementById('statusMsg').className = 'status-msg success';
            document.getElementById('btnDownload').disabled = false;

            const saveUrl = '/api/file?id=' + currentJobId;
            document.getElementById('saveLink').href = saveUrl;
            document.getElementById('savePrompt').style.display = 'block';

            // Trigger otomatis unduhan ke browser Android
            const a = document.createElement('a');
            a.href = saveUrl;
            a.download = '';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          } else if (data.state === 'error') {
            clearInterval(pollInterval);
            document.getElementById('statusMsg').innerText = '✕ ' + (data.error || 'Gagal');
            document.getElementById('statusMsg').className = 'status-msg error';
            document.getElementById('btnDownload').disabled = false;
          }
        } catch (e) {}
      }, 1000);
    }
  </script>
</body>
</html>
"""


class WebHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Diam agar konsol tetap bersih
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            data = HTML_TEMPLATE.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path == "/api/ip":
            self._send_json({"ip": get_local_ip()})
            return

        if path == "/api/info":
            url = query.get("url", [None])[0]
            if not url:
                self._send_json({"error": "URL tidak disertakan"}, status=400)
                return
            try:
                info = core.fetch_info(url)
                sizes_fmt = {k: core.human_size(v) for k, v in info.sizes.items()}
                res = {
                    "url": info.url,
                    "title": info.title,
                    "uploader": info.uploader,
                    "duration": info.duration,
                    "duration_fmt": core.fmt_duration(info.duration),
                    "thumbnail": info.thumbnail,
                    "platform": info.platform,
                    "heights": info.heights,
                    "sizes": sizes_fmt,
                    "has_video": info.has_video,
                }
                self._send_json(res)
            except Exception as e:
                self._send_json({"error": core.clean_error(e)}, status=500)
            return

        if path == "/api/status":
            job_id = query.get("id", [None])[0]
            with _jobs_lock:
                job = _web_jobs.get(job_id)
            if not job:
                self._send_json({"error": "Job tidak ditemukan"}, status=404)
                return
            self._send_json(job.get("data", {"state": "queued"}))
            return

        if path == "/api/file":
            job_id = query.get("id", [None])[0]
            with _jobs_lock:
                job = _web_jobs.get(job_id)
            if not job or not job.get("filepath") or not os.path.isfile(job["filepath"]):
                self._send_json({"error": "File belum siap atau tidak ditemukan"}, status=404)
                return

            filepath = job["filepath"]
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            mime, _ = mimetypes.guess_type(filepath)
            mime = mime or "application/octet-stream"

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(filesize))
            safe_name = urllib.parse.quote(filename)
            self.send_header("Content-Disposition", f'attachment; filename="{safe_name}"; filename*=UTF-8\'\'{safe_name}')
            self.end_headers()

            with open(filepath, "rb") as f:
                while chunk := f.read(64 * 1024):
                    self.wfile.write(chunk)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/download":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                self._send_json({"error": "JSON tidak valid"}, status=400)
                return

            url = payload.get("url")
            title = payload.get("title") or "video"
            mode = payload.get("mode", "video")
            quality = payload.get("quality")

            settings = Settings()
            out_dir = settings.get("output_dir")

            job_id = f"job_{int(time.time() * 1000)}"
            with _jobs_lock:
                _web_jobs[job_id] = {
                    "id": job_id,
                    "filepath": None,
                    "data": {"state": "starting", "progress": 0},
                }

            def _callback(job: core.DownloadJob, data: dict):
                with _jobs_lock:
                    if job_id in _web_jobs:
                        _web_jobs[job_id]["data"].update(data)
                        if data.get("filepath"):
                            _web_jobs[job_id]["filepath"] = data["filepath"]
                        if data.get("speed"):
                            _web_jobs[job_id]["data"]["speed"] = core.human_size(data["speed"]) + "/s"
                        if data.get("eta") is not None:
                            _web_jobs[job_id]["data"]["eta"] = core.fmt_duration(data["eta"])

            job = core.DownloadJob(
                url=url,
                title=title,
                mode=mode,
                quality=quality,
                out_dir=out_dir,
                playlist=False,
                cookies_browser=None,
                callback=_callback,
            )

            threading.Thread(target=job.run, daemon=True).start()
            self._send_json({"job_id": job_id, "status": "queued"})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _send_json(self, data: dict, status: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)


def start_server(port: int = 8080) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("0.0.0.0", port), WebHandler)
    return server
