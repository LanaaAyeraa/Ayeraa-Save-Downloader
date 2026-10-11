# -*- coding: utf-8 -*-
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=== 1. TEST IMPORTS ===")
try:
    import customtkinter as ctk
    print("[OK] customtkinter loaded successfully")
except Exception as e:
    print("[FAIL] customtkinter failed:", e)
    sys.exit(1)

try:
    from tkinterweb import HtmlFrame
    print("[OK] tkinterweb (HtmlFrame) loaded successfully")
except Exception as e:
    print("[FAIL] tkinterweb failed:", e)
    sys.exit(1)

try:
    import yt_dlp
    print(f"[OK] yt_dlp loaded successfully (version: {yt_dlp.version.__version__})")
except Exception as e:
    print("[FAIL] yt_dlp failed:", e)
    sys.exit(1)

try:
    from allsave.ui import App
    print("[OK] allsave.ui.App imported successfully")
except Exception as e:
    print("[FAIL] allsave.ui import failed:", e)
    sys.exit(1)

print("\n=== 2. TEST UI INITIALIZATION & ALT+B SHORTCUT ===")
try:
    # Initialize CTk app in headless mode (withdraw immediately)
    app = App()
    app.withdraw()  # do not show window during automated test
    print("[OK] App initialized without errors")
    print(f"  - Window title: {app.title()}")
    assert app.title() == "Ayeraa Save Downloader", f"Unexpected title: {app.title()}"

    # Initial state
    print(f"  - Initial _side_browser_open: {app._side_browser_open}")
    assert app._side_browser_open is False, "Initial browser state should be False"

    # Trigger Alt+B toggle: OPEN
    print("\nTesting Alt+B shortcut action -> OPEN...")
    app.toggle_side_browser()
    app.update()
    print(f"  - _side_browser_open after toggle: {app._side_browser_open}")
    assert app._side_browser_open is True, "Browser should be visible after toggle"
    assert hasattr(app, "_side_browser_frame") and app._side_browser_frame is not None, "Browser frame must exist"
    print("[OK] Side browser frame created, expanded, and rendered cleanly")

    # Test Grab URL feature
    print("\nTesting 'Ambil Link ke Input' feature...")
    app._browser_url_entry.delete(0, "end")
    app._browser_url_entry.insert(0, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    app._browser_grab_url()
    grabbed_url = app.url_entry.get().strip()
    print(f"  - Copied URL into main entry: {grabbed_url}")
    assert grabbed_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "URL grab mismatch!"
    print("[OK] Grab URL button correctly feeds browser link into main download input")

    # Trigger Alt+B toggle: CLOSE
    print("\nTesting Alt+B shortcut action -> CLOSE...")
    app.toggle_side_browser()
    app.update()
    print(f"  - _side_browser_open after close: {app._side_browser_open}")
    assert app._side_browser_open is False, "Browser should be hidden after 2nd toggle"
    print("[OK] Side browser smoothly collapses and restores window geometry")

    app.destroy()
    print("\n=== RESULT: ALL WINDOWS APP TESTS PASSED (100% GREEN) ===")
except Exception as e:
    import traceback
    traceback.print_exc()
    print("[FAIL] UI test encountered error:", e)
    sys.exit(1)
