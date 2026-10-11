"""Konfigurasi & penyimpanan pengaturan aplikasi."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

APP_NAME = "Ayeraa Save Downloader"
APP_ID = "AyeraaSaveDownloader"
VERSION = "1.2.0"


def app_data_dir() -> Path:
    """Folder data aplikasi (%APPDATA%/AyeraaSaveDownloader)."""
    base = os.environ.get("APPDATA") or str(Path.home())
    path = Path(base) / APP_ID
    path.mkdir(parents=True, exist_ok=True)
    return path


def resource_path(relative: str) -> Path:
    """Path ke resource, kompatibel dengan mode script maupun .exe (PyInstaller)."""
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        base = Path(__file__).resolve().parent.parent
    return Path(base) / relative


DEFAULTS = {
    "output_dir": str(Path.home() / "Downloads" / "AyeraaSave"),
    "cookies_browser": "Tidak ada",
    "max_concurrent": 2,
    "last_mode": "Video MP4",
}


class Settings:
    def __init__(self) -> None:
        self.path = app_data_dir() / "settings.json"
        self.data = dict(DEFAULTS)
        try:
            self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
        except Exception:
            pass

    def get(self, key: str):
        return self.data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value) -> None:
        self.data[key] = value
        self.save()

    def save(self) -> None:
        try:
            self.path.write_text(
                json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception:
            pass
