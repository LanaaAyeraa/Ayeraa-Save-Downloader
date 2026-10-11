"""Modul Auto-Update otomatis untuk Windows (Ayeraa Save Downloader)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from typing import Callable, Optional

from .config import APP_NAME, VERSION

GITHUB_REPO = "LanaaAyeraa/Ayeraa-Save-Downloader"
CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def compare_versions(remote_tag: str, current_ver: str) -> int:
    """Bandingkan versi remote vs lokal. Return 1 jika remote lebih baru."""
    clean_r = remote_tag.lstrip("vV").strip()
    clean_c = current_ver.lstrip("vV").strip()

    r_parts = [int(p) if p.isdigit() else 0 for p in clean_r.split(".")[:3]]
    c_parts = [int(p) if p.isdigit() else 0 for p in clean_c.split(".")[:3]]

    while len(r_parts) < 3:
        r_parts.append(0)
    while len(c_parts) < 3:
        c_parts.append(0)

    if r_parts > c_parts:
        return 1
    elif r_parts < c_parts:
        return -1
    return 0


def check_for_updates() -> Optional[dict]:
    """Cek rilis terbaru dari GitHub API."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Ayeraa-Save-Downloader-Windows",
            "Accept": "application/vnd.github.v3+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("[Updater] Cek rilis gagal:", e)
        return None

    tag = data.get("tag_name", "")
    if not tag:
        return None

    if compare_versions(tag, VERSION) <= 0:
        return None

    assets = data.get("assets", [])
    download_url = None
    target_name = None
    size = 0

    # Prioritas: Setup.exe / Ayeraa Save Downloader.exe
    for a in assets:
        name = a.get("name", "")
        if name.endswith(".exe") and "Setup" in name:
            download_url = a.get("browser_download_url")
            target_name = name
            size = a.get("size", 0)
            break

    if not download_url:
        for a in assets:
            name = a.get("name", "")
            if name.endswith(".exe"):
                download_url = a.get("browser_download_url")
                target_name = name
                size = a.get("size", 0)
                break

    if not download_url:
        return None

    return {
        "tag": tag,
        "version": tag.lstrip("vV"),
        "title": data.get("name", tag),
        "body": data.get("body", "Pembaruan versi terbaru untuk Ayeraa Save Downloader."),
        "download_url": download_url,
        "asset_name": target_name,
        "size": size,
    }


def download_update(
    url: str,
    dest_path: str,
    progress_callback: Optional[Callable[[int, int, int], None]] = None,
) -> bool:
    """Download file update dengan tracking progress."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Ayeraa-Save-Downloader"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 64 * 1024
            last_report = 0

            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    now = time.time()
                    if now - last_report > 0.15 or downloaded == total:
                        last_report = now
                        percent = int((downloaded * 100) / total) if total > 0 else 50
                        if progress_callback:
                            progress_callback(percent, downloaded, total)
        return True
    except Exception as e:
        print("[Updater] Download gagal:", e)
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                pass
        return False


def apply_update_and_restart(temp_installer_or_exe: str) -> None:
    """Terapkan update dan restart aplikasi tanpa instal ulang manual."""
    current_exe = sys.executable

    # Jika berjalan dari .exe (PyInstaller standalone)
    if getattr(sys, "frozen", False) and current_exe.lower().endswith(".exe"):
        # Jika file download adalah installer setup (.exe)
        if "setup" in os.path.basename(temp_installer_or_exe).lower():
            cmd = f'start "" "{temp_installer_or_exe}" /SILENT'
            bat_content = f"""@echo off
timeout /t 2 /nobreak > nul
start "" "{temp_installer_or_exe}" /SILENT
exit
"""
        else:
            # Ganti file EXE secara langsung
            bat_content = f"""@echo off
timeout /t 2 /nobreak > nul
copy /y "{temp_installer_or_exe}" "{current_exe}" > nul
del /f /q "{temp_installer_or_exe}" > nul
start "" "{current_exe}"
del /f /q "%~f0" > nul
exit
"""
        bat_file = os.path.join(tempfile.gettempdir(), "ayeraa_updater.bat")
        with open(bat_file, "w", encoding="utf-8") as f:
            f.write(bat_content)

        subprocess.Popen(
            ["cmd.exe", "/c", bat_file],
            creationflags=CREATE_NO_WINDOW,
            close_fds=True,
        )
        sys.exit(0)
    else:
        # Development mode / testing
        os.startfile(temp_installer_or_exe)
        sys.exit(0)
