"""Unit tests for Ayeraa Browser Navigator window logic."""
import json
import unittest
from unittest.mock import MagicMock

from allsave.browser_window import BrowserApi, get_injected_hud_js, get_start_page_html
from allsave.ipc import IPCServer


class TestBrowserWindow(unittest.TestCase):
    def test_start_page_html_content(self) -> None:
        html = get_start_page_html(48231)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Ayeraa Browser Navigator", html)
        self.assertIn("navInput", html)
        self.assertIn("https://www.youtube.com", html)
        self.assertIn("https://www.tiktok.com", html)
        self.assertIn("https://www.instagram.com", html)
        self.assertIn("https://x.com", html)

    def test_injected_hud_js_contains_ipc_port_and_shadow_dom(self) -> None:
        js = get_injected_hud_js(54321)
        self.assertIn("const IPC_PORT = 54321;", js)
        self.assertIn("attachShadow", js)
        self.assertIn("btnGrab", js)
        self.assertIn("btnBack", js)
        self.assertIn("btnHome", js)
        self.assertIn("btnMin", js)

    def test_browser_api_grab_url_notifies_ipc(self) -> None:
        received = []
        server = IPCServer(on_grab_url=lambda u: received.append(u), port=0)
        port = server.start()
        try:
            mock_win = MagicMock()
            api = BrowserApi(window=mock_win, ipc_port=port)
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            res = api.grab_url(test_url)
            self.assertEqual(res.get("status"), "ok")
            self.assertEqual(res.get("url"), test_url)
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0], test_url)
        finally:
            server.stop()

    def test_browser_api_navigate_url_formatting(self) -> None:
        mock_win = MagicMock()
        api = BrowserApi(window=mock_win, ipc_port=48231)

        # 1. Plain search term
        res1 = api.navigate("resep martabak manis")
        self.assertIn("google.com/search?q=", res1["target"])
        mock_win.load_url.assert_called_with(res1["target"])

        # 2. Domain without scheme
        res2 = api.navigate("youtube.com")
        self.assertEqual(res2["target"], "https://youtube.com")
        mock_win.load_url.assert_called_with("https://youtube.com")

        # 3. Full URL
        res3 = api.navigate("https://instagram.com/p/123")
        self.assertEqual(res3["target"], "https://instagram.com/p/123")
        mock_win.load_url.assert_called_with("https://instagram.com/p/123")


if __name__ == "__main__":
    unittest.main()
