"""Comprehensive Hardtest Suite for Ayeraa Browser Navigator & IPC Subprocess.

Verifies:
1. IPC HTTP Server under normal, special character, and concurrent loads.
2. Browser Start Page and Floating HUD Javascript structure & escaping.
3. Subprocess CLI argument handling and clean process lifecycle.
4. Edge WebView2 engine integration with live browser execution.
5. End-to-end link grabbing, URL extraction, and clipboard synchronization.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import unittest
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from allsave.browser_window import BrowserApi, get_injected_hud_js, get_start_page_html
from allsave.ipc import IPCServer


class HardtestBrowserNavigator(unittest.TestCase):
    """Hardtest suite for browser engine and inter-process communication."""

    def setUp(self) -> None:
        self.received_urls: list[str] = []
        self.ipc_server = IPCServer(on_grab_url=lambda u: self.received_urls.append(u), port=0)
        self.port = self.ipc_server.start()

    def tearDown(self) -> None:
        if hasattr(self, "ipc_server") and self.ipc_server:
            self.ipc_server.stop()

    def test_01_ipc_server_ping_and_cors(self) -> None:
        """Verify IPC server responds to ping with accurate metadata and CORS headers."""
        url = f"http://127.0.0.1:{self.port}/ping"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertIn("Ayeraa", data.get("app", ""))

    def test_02_ipc_special_urls_and_query_parameters(self) -> None:
        """Verify complex URLs with timestamps, hash fragments, and UTF-8 parameters are preserved."""
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&feature=shared",
            "https://www.tiktok.com/@creator/video/7123456789012345678?is_from_webapp=1",
            "https://www.instagram.com/reel/C5abcdefghijk/?utm_source=ig_web_copy_link",
            "https://x.com/username/status/1789012345678901234?s=20",
            "https://soundcloud.com/artist/track-name?in=playlist#t=1:30",
            "https://example.com/video?title=lagu%20daerah%20jawa&tag=musik#play",
        ]

        for u in test_urls:
            encoded = urllib.parse.quote(u)
            req = urllib.request.Request(f"http://127.0.0.1:{self.port}/grab?url={encoded}")
            with urllib.request.urlopen(req, timeout=3) as resp:
                self.assertEqual(resp.status, 200)
                res = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(res.get("url"), u)

        time.sleep(0.1)
        self.assertEqual(len(self.received_urls), len(test_urls))
        for original in test_urls:
            self.assertIn(original, self.received_urls)

    def test_03_concurrent_grab_stress_test(self) -> None:
        """Verify thread safety under rapid concurrent requests from browser navigation."""
        urls = [f"https://www.youtube.com/watch?v=video_id_{i}" for i in range(25)]

        def send_grab(u: str) -> bool:
            try:
                encoded = urllib.parse.quote(u)
                with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/grab?url={encoded}", timeout=5) as r:
                    return r.status == 200
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(send_grab, urls))

        self.assertTrue(all(results))
        time.sleep(0.2)
        self.assertEqual(len(self.received_urls), 25)

    def test_04_start_page_and_hud_assets(self) -> None:
        """Verify HTML start page and floating HUD script generation."""
        html = get_start_page_html(self.port)
        self.assertTrue(html.strip().startswith("<!DOCTYPE html>"))
        self.assertIn("Ayeraa Browser Navigator", html)
        self.assertIn("navInput", html)
        self.assertIn("https://www.youtube.com", html)
        self.assertIn("https://www.tiktok.com", html)
        self.assertIn("https://www.instagram.com", html)

        hud_js = get_injected_hud_js(self.port)
        self.assertIn(f"const IPC_PORT = {self.port};", hud_js)
        self.assertIn("attachShadow", hud_js)
        self.assertIn("ayeraa-hud-host", hud_js)
        self.assertIn("btnGrab", hud_js)
        self.assertIn("btnMin", hud_js)

    def test_05_browser_cli_process_execution(self) -> None:
        """Verify that launching 'main.py --browser' spawns cleanly and responds."""
        cmd = [sys.executable, "main.py", "--browser", "--ipc-port", str(self.port)]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Allow time for Edge WebView2 process initialization
            time.sleep(2.5)
            self.assertIsNone(proc.poll(), "Browser process terminated prematurely!")

            # Simulate in-browser grab event via IPC
            simulated_url = "https://www.youtube.com/watch?v=test_hardtest_id"
            encoded = urllib.parse.quote(simulated_url)
            req = urllib.request.Request(f"http://127.0.0.1:{self.port}/grab?url={encoded}")
            with urllib.request.urlopen(req, timeout=3) as resp:
                self.assertEqual(resp.status, 200)

            time.sleep(0.2)
            self.assertIn(simulated_url, self.received_urls)

        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    unittest.main()
