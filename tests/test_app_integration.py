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
            # Verify Alt-B event bindings exist on root
            bound_b = app.bind_all("<Alt-b>")
            bound_cap_b = app.bind_all("<Alt-B>")
            self.assertTrue(bool(bound_b))
            self.assertTrue(bool(bound_cap_b))
            # Test IPC url application
            test_url = "https://www.youtube.com/watch?v=integration_test"
            app._apply_grabbed_url(test_url)
            self.assertEqual(app.url_entry.get(), test_url)
        finally:
            app._on_close()


if __name__ == "__main__":
    unittest.main()
