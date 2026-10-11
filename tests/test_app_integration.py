"""Integration test for allsave App initialization and IPC integration."""
import unittest

from allsave.ui import App


class TestAppIntegration(unittest.TestCase):
    def test_app_init_and_destroy(self) -> None:
        app = App()
        try:
            self.assertIsNotNone(app._ipc_server)
            self.assertGreater(app._ipc_port, 0)
            self.assertTrue(hasattr(app, "toggle_side_browser"))
            # Test IPC url application
            test_url = "https://www.youtube.com/watch?v=integration_test"
            app._apply_grabbed_url(test_url)
            self.assertEqual(app.url_entry.get(), test_url)
        finally:
            app._on_close()


if __name__ == "__main__":
    unittest.main()
