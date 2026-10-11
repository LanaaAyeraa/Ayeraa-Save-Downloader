"""Unit tests for Ayeraa Save Downloader IPC communication."""
import json
import time
import unittest
import urllib.parse
import urllib.request

from allsave.ipc import IPCServer


class TestIPCServer(unittest.TestCase):
    def setUp(self) -> None:
        self.received_urls: list[str] = []
        self.server = IPCServer(on_grab_url=lambda u: self.received_urls.append(u), port=0)
        self.port = self.server.start()

    def tearDown(self) -> None:
        self.server.stop()

    def test_ping_endpoint(self) -> None:
        url = f"http://127.0.0.1:{self.port}/ping"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertIn("Ayeraa", data.get("app", ""))

    def test_grab_endpoint_via_get(self) -> None:
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        encoded = urllib.parse.quote(test_url)
        url = f"http://127.0.0.1:{self.port}/grab?url={encoded}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertEqual(data.get("url"), test_url)

        time.sleep(0.1)
        self.assertEqual(len(self.received_urls), 1)
        self.assertEqual(self.received_urls[0], test_url)

    def test_grab_endpoint_via_post(self) -> None:
        test_url = "https://www.tiktok.com/@user/video/1234567890"
        payload = json.dumps({"url": test_url}).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/grab",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertEqual(data.get("url"), test_url)

        time.sleep(0.1)
        self.assertIn(test_url, self.received_urls)


if __name__ == "__main__":
    unittest.main()
