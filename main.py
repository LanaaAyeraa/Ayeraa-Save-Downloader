"""Entry point Ayeraa Save Downloader."""
import os
import sys

# Mode .exe tanpa konsol: stdout/stderr bernilai None -> arahkan ke devnull
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

# Tampilan tajam di layar HiDPI & ikon taskbar sendiri
if sys.platform == "win32":
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AyeraaSave.Downloader")
    except Exception:
        pass

if "--browser" in sys.argv:
    from allsave.browser_window import run_browser_cli

    run_browser_cli()
    sys.exit(0)

from allsave.ui import App  # noqa: E402


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
