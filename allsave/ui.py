"""Antarmuka grafis AllSave Downloader (customtkinter)."""
from __future__ import annotations

import io
import os
import queue
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog, messagebox
from typing import Optional
import urllib.parse
import webbrowser

from .ipc import IPCServer

import customtkinter as ctk
from PIL import Image, ImageDraw

from . import core, web
from .branding import make_logo
from .config import APP_NAME, VERSION, Settings, resource_path

# --------------------------------------------------------------------------- #
# Palet warna
# --------------------------------------------------------------------------- #
BG = "#0E1014"
CARD = "#171A21"
CARD_2 = "#1F232C"
BORDER = "#2A2F3A"
TEXT = "#EDEFF3"
MUTED = "#8B93A1"
ACCENT = "#FF3D6E"
ACCENT_HOVER = "#E02A5A"
SUCCESS = "#22C55E"
SUCCESS_HOVER = "#16A34A"
DANGER = "#EF4444"
WARN = "#F59E0B"

MODES = ["Video MP4", "Audio MP3", "Audio M4A"]
MODE_KEYS = {"Video MP4": "video", "Audio MP3": "mp3", "Audio M4A": "m4a"}
BROWSERS = ["Tidak ada", "firefox", "chrome", "edge", "brave", "opera", "vivaldi"]
CHIPS = ["YouTube", "TikTok", "Instagram", "Facebook", "X / Twitter", "SoundCloud", "Vimeo", "+1000 situs"]

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def _font(size: int = 13, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)


def _shorten(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _quality_tag(h: int) -> str:
    if h >= 2160:
        return "4K"
    if h >= 1440:
        return "2K"
    if h >= 1080:
        return "Full HD"
    if h >= 720:
        return "HD"
    return ""


def _placeholder_thumb(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), CARD_2)
    d = ImageDraw.Draw(img)
    cx, cy, r = w // 2, h // 2, min(w, h) // 6
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#2C313C")
    d.polygon([(cx - r // 3, cy - r // 2), (cx - r // 3, cy + r // 2), (cx + r // 2, cy)], fill=MUTED)
    return img


def _fit_cover(img: Image.Image, w: int, h: int) -> Image.Image:
    """Crop gambar agar memenuhi kotak w x h (seperti CSS object-fit: contain dengan latar)."""
    img = img.convert("RGB")
    canvas = Image.new("RGB", (w, h), "#000000")
    ratio = min(w / img.width, h / img.height)
    new = img.resize((max(1, int(img.width * ratio)), max(1, int(img.height * ratio))), Image.LANCZOS)
    canvas.paste(new, ((w - new.width) // 2, (h - new.height) // 2))
    return canvas


# --------------------------------------------------------------------------- #
# Kartu item antrian
# --------------------------------------------------------------------------- #
class JobCard(ctk.CTkFrame):
    def __init__(self, master, app: "App", job: core.DownloadJob) -> None:
        super().__init__(master, fg_color=CARD_2, corner_radius=12, border_width=1, border_color=BORDER)
        self.app = app
        self.job = job
        self.grid_columnconfigure(1, weight=1)

        self.tag = ctk.CTkLabel(
            self, text=job.label, font=_font(11, "bold"), fg_color=ACCENT if job.mode == "video" else "#7C3AED",
            text_color="white", corner_radius=6, width=86, height=22,
        )
        self.tag.grid(row=0, column=0, padx=(12, 8), pady=(12, 2), sticky="w")

        self.title = ctk.CTkLabel(
            self, text=_shorten(job.title, 80), font=_font(13, "bold"), text_color=TEXT, anchor="w"
        )
        self.title.grid(row=0, column=1, sticky="we", pady=(12, 2))

        self.btns = ctk.CTkFrame(self, fg_color="transparent")
        self.btns.grid(row=0, column=2, rowspan=3, padx=12, pady=10, sticky="e")

        self.progress = ctk.CTkProgressBar(self, height=8, corner_radius=4, progress_color=ACCENT, fg_color=BORDER)
        self.progress.set(0)
        self.progress.grid(row=1, column=0, columnspan=2, sticky="we", padx=12, pady=(6, 4))

        self.status = ctk.CTkLabel(
            self, text="Menunggu antrian...", font=_font(12), text_color=MUTED, anchor="w", justify="left"
        )
        self.status.grid(row=2, column=0, columnspan=2, sticky="we", padx=12, pady=(0, 10))

        self._indeterminate = False
        self._set_buttons("active")

    # -- tombol ----------------------------------------------------------- #
    def _btn(self, text: str, cmd, color: str = CARD, hover: str = BORDER, width: int = 84) -> ctk.CTkButton:
        b = ctk.CTkButton(
            self.btns, text=text, command=cmd, width=width, height=30, corner_radius=8,
            fg_color=color, hover_color=hover, font=_font(12, "bold"), border_width=1, border_color=BORDER,
        )
        b.pack(side="left", padx=3)
        return b

    def _set_buttons(self, kind: str) -> None:
        for w in self.btns.winfo_children():
            w.destroy()
        if kind == "active":
            self._btn("✕  Batal", self.job.cancel)
        elif kind == "done":
            if self.job.filepath and os.path.isfile(self.job.filepath) and not self.job.playlist:
                self._btn("▶  Buka", self._open_file, SUCCESS, SUCCESS_HOVER)
            self._btn("Folder", self._open_folder)
            self._btn("✕", self.remove, width=34)
        else:  # error / cancelled
            self._btn("⟳  Ulangi", self._retry, ACCENT, ACCENT_HOVER)
            self._btn("✕", self.remove, width=34)

    def _open_file(self) -> None:
        try:
            os.startfile(self.job.filepath)  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(APP_NAME, f"Tidak bisa membuka file:\n{exc}")

    def _open_folder(self) -> None:
        path = self.job.filepath
        if path and os.path.exists(path):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        else:
            self.app.open_output_folder(self.job.out_dir)

    def _retry(self) -> None:
        self.remove()
        self.app.submit_job(self.job.clone())

    def remove(self) -> None:
        self.app.remove_card(self)

    # -- update status ---------------------------------------------------- #
    def _set_indeterminate(self, on: bool) -> None:
        if on and not self._indeterminate:
            self.progress.configure(mode="indeterminate")
            self.progress.start()
        elif not on and self._indeterminate:
            self.progress.stop()
            self.progress.configure(mode="determinate")
        self._indeterminate = on

    def update_state(self, data: dict) -> None:
        state = data.get("state")
        item = data.get("item")
        prefix = ""
        if item and item[0]:
            prefix = f"[{item[0]}/{item[1] or '?'}]  "

        if state == "starting":
            self._set_indeterminate(True)
            self.status.configure(text="Menyiapkan download...", text_color=MUTED)
        elif state == "downloading":
            frac = data.get("progress")
            if frac is None:
                self._set_indeterminate(True)
                parts = [f"{prefix}Mengunduh", core.human_size(data.get("downloaded"))]
            else:
                self._set_indeterminate(False)
                self.progress.set(frac)
                parts = [f"{prefix}Mengunduh {frac * 100:.0f}%"]
                if data.get("total"):
                    parts.append(f"{core.human_size(data.get('downloaded'))} / {core.human_size(data['total'])}")
            if data.get("speed"):
                parts.append(f"{core.human_size(data['speed'])}/s")
            if data.get("eta") is not None:
                parts.append(f"sisa {core.fmt_duration(data['eta'])}")
            self.status.configure(text="  •  ".join(parts), text_color=MUTED)
        elif state == "processing":
            self._set_indeterminate(True)
            self.status.configure(text=prefix + data.get("text", "Memproses..."), text_color=WARN)
        elif state == "done":
            self._set_indeterminate(False)
            self.progress.set(1)
            self.progress.configure(progress_color=SUCCESS)
            name = os.path.basename(self.job.filepath) if self.job.filepath and not self.job.playlist else ""
            text = "✓  Selesai" + (f"  —  {_shorten(name, 70)}" if name else f"  —  tersimpan di {self.job.out_dir}")
            self.status.configure(text=text, text_color=SUCCESS)
            self._set_buttons("done")
        elif state == "cancelled":
            self._set_indeterminate(False)
            self.progress.configure(progress_color=MUTED)
            self.status.configure(text="Dibatalkan", text_color=MUTED)
            self._set_buttons("retry")
        elif state == "error":
            self._set_indeterminate(False)
            self.progress.configure(progress_color=DANGER)
            self.progress.set(1)
            err = data.get("error", "Gagal")
            self.status.configure(text="✕  " + err.split("\n")[0][:160], text_color=DANGER)
            self._set_buttons("retry")


# --------------------------------------------------------------------------- #
# Jendela utama
# --------------------------------------------------------------------------- #
class App(ctk.CTk):
    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__(fg_color=BG)
        self.settings = Settings()
        self.title(f"{APP_NAME}")
        self.geometry("1040x760")
        self.minsize(900, 640)
        try:
            self.iconbitmap(str(resource_path("assets/icon.ico")))
        except Exception:
            pass

        self.ui_queue: "queue.Queue[tuple]" = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=int(self.settings.get("max_concurrent") or 2))
        self.cards: dict[int, JobCard] = {}
        self.current_info: Optional[core.MediaInfo] = None
        self._quality_map: dict[str, Optional[int]] = {}
        self._thumb_image: Optional[ctk.CTkImage] = None
        self._analyzing = False
        self._web_server = None
        self._web_port = 8080

        self._browser_process: Optional[subprocess.Popen] = None
        self._ipc_server = IPCServer(on_grab_url=self._on_ipc_grab_url)
        self._ipc_port = self._ipc_server.start()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self._build_header()
        self._build_input()
        self._build_preview()
        self._build_queue()
        self._build_footer()

        self.bind("<Return>", lambda _e: self.analyze())
        self.bind_all("<Alt-b>", lambda _e: self.toggle_side_browser())
        self.bind_all("<Alt-B>", lambda _e: self.toggle_side_browser())
        self.bind_all("<Alt-KeyPress-b>", lambda _e: self.toggle_side_browser())
        self.bind_all("<Alt-KeyPress-B>", lambda _e: self.toggle_side_browser())
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(80, self._poll_queue)
        threading.Thread(target=self._init_ffmpeg, daemon=True).start()
        self.after(300, self.url_entry.focus_set)

    # ------------------------------------------------------------------ UI #
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="we", padx=24, pady=(20, 10))
        header.grid_columnconfigure(1, weight=1)

        logo = ctk.CTkImage(make_logo(96), size=(48, 48))
        ctk.CTkLabel(header, text="", image=logo).grid(row=0, column=0, rowspan=2, padx=(0, 14))
        title = ctk.CTkFrame(header, fg_color="transparent")
        title.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(title, text="Ayeraa Save", font=_font(26, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(title, text=" Downloader", font=_font(26), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(
            header,
            text="Download video & audio dari semua platform — cepat, gratis, tanpa iklan.",
            font=_font(13), text_color=MUTED,
        ).grid(row=1, column=1, sticky="w")
        
        top_right = ctk.CTkFrame(header, fg_color="transparent")
        top_right.grid(row=0, column=2, rowspan=2, sticky="ne")

        ctk.CTkButton(
            top_right, text="📱 Buka di HP", font=_font(12, "bold"), fg_color=CARD_2, hover_color=BORDER,
            border_width=1, border_color=BORDER, height=32, width=110, command=self.open_mobile_modal
        ).pack(side="top", anchor="e", pady=(0, 4))

        ctk.CTkLabel(top_right, text=f"v{VERSION}", font=_font(11), text_color=MUTED).pack(side="top", anchor="e")

    def _build_input(self) -> None:
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        card.grid(row=1, column=0, sticky="we", padx=24, pady=6)
        card.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(
            card, placeholder_text="Tempel link video di sini…  (YouTube, TikTok, Instagram, Facebook, X, dll.)",
            height=50, font=_font(14), corner_radius=12, border_width=1, border_color=BORDER, fg_color=BG,
        )
        self.url_entry.grid(row=0, column=0, sticky="we", padx=(16, 8), pady=(16, 8))

        ctk.CTkButton(
            card, text="Tempel", width=96, height=50, corner_radius=12, font=_font(13, "bold"),
            fg_color=CARD_2, hover_color=BORDER, border_width=1, border_color=BORDER, command=self.paste_url,
        ).grid(row=0, column=1, padx=4, pady=(16, 8))

        self.analyze_btn = ctk.CTkButton(
            card, text="Mulai  →", width=140, height=50, corner_radius=12, font=_font(15, "bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER, command=self.analyze,
        )
        self.analyze_btn.grid(row=0, column=2, padx=(4, 16), pady=(16, 8))

        self.analyze_bar = ctk.CTkProgressBar(card, height=3, mode="indeterminate", progress_color=ACCENT, fg_color=CARD)
        self.analyze_bar.grid(row=1, column=0, columnspan=3, sticky="we", padx=16)
        self.analyze_bar.grid_remove()

        opts = ctk.CTkFrame(card, fg_color="transparent")
        opts.grid(row=2, column=0, columnspan=3, sticky="we", padx=16, pady=(6, 14))

        self.playlist_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            opts, text="Unduh seluruh playlist", variable=self.playlist_var, font=_font(12),
            fg_color=ACCENT, hover_color=ACCENT_HOVER, checkbox_width=18, checkbox_height=18, border_width=2,
        ).pack(side="left")

        ctk.CTkLabel(opts, text="Cookies dari browser:", font=_font(12), text_color=MUTED).pack(side="left", padx=(24, 6))
        self.cookies_menu = ctk.CTkOptionMenu(
            opts, values=BROWSERS, width=120, height=28, font=_font(12), fg_color=CARD_2,
            button_color=BORDER, button_hover_color=ACCENT, command=lambda v: self.settings.set("cookies_browser", v),
        )
        self.cookies_menu.set(self.settings.get("cookies_browser"))
        self.cookies_menu.pack(side="left")
        ctk.CTkLabel(
            opts, text="(untuk konten yang butuh login)", font=_font(11), text_color=MUTED
        ).pack(side="left", padx=6)

        chips = ctk.CTkFrame(opts, fg_color="transparent")
        chips.pack(side="right")
        for name in CHIPS[:5] + CHIPS[-1:]:
            ctk.CTkLabel(
                chips, text=name, font=_font(11), fg_color=CARD_2, corner_radius=8, text_color=MUTED, height=22,
            ).pack(side="left", padx=2, ipadx=6)

    def _build_preview(self) -> None:
        self.preview_holder = ctk.CTkFrame(self, fg_color="transparent")
        self.preview_holder.grid(row=2, column=0, sticky="we", padx=24, pady=6)
        self.preview_holder.grid_columnconfigure(0, weight=1)

        # --- Empty state ---
        self.empty_card = ctk.CTkFrame(self.preview_holder, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        self.empty_card.grid(row=0, column=0, sticky="we")
        steps = ctk.CTkFrame(self.empty_card, fg_color="transparent")
        steps.pack(pady=18)
        for i, (head, sub) in enumerate(
            [
                ("Salin link", "dari aplikasi/website mana pun"),
                ("Tempel & Mulai", "tekan Enter atau tombol Mulai"),
                ("Pilih format", "MP4 hingga 4K atau MP3 320kbps"),
            ],
            start=1,
        ):
            box = ctk.CTkFrame(steps, fg_color="transparent")
            box.pack(side="left", padx=26)
            ctk.CTkLabel(
                box, text=str(i), width=34, height=34, corner_radius=17, fg_color=ACCENT,
                text_color="white", font=_font(15, "bold"),
            ).pack(side="left", padx=(0, 10))
            txt = ctk.CTkFrame(box, fg_color="transparent")
            txt.pack(side="left")
            ctk.CTkLabel(txt, text=head, font=_font(13, "bold"), text_color=TEXT, anchor="w").pack(anchor="w")
            ctk.CTkLabel(txt, text=sub, font=_font(11), text_color=MUTED, anchor="w").pack(anchor="w")

        # --- Preview card ---
        self.preview = ctk.CTkFrame(self.preview_holder, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        self.preview.grid_columnconfigure(1, weight=1)

        self._placeholder = ctk.CTkImage(_placeholder_thumb(320, 180), size=(256, 144))
        self.thumb_label = ctk.CTkLabel(self.preview, text="", image=self._placeholder, corner_radius=10)
        self.thumb_label.grid(row=0, column=0, rowspan=4, padx=16, pady=16, sticky="n")

        top = ctk.CTkFrame(self.preview, fg_color="transparent")
        top.grid(row=0, column=1, sticky="we", padx=(0, 16), pady=(16, 0))
        self.platform_badge = ctk.CTkLabel(
            top, text="YouTube", font=_font(11, "bold"), fg_color=ACCENT, text_color="white", corner_radius=6, height=22
        )
        self.platform_badge.pack(side="left", ipadx=8)
        self.meta_label = ctk.CTkLabel(top, text="", font=_font(12), text_color=MUTED)
        self.meta_label.pack(side="left", padx=10)

        self.title_label = ctk.CTkLabel(
            self.preview, text="", font=_font(16, "bold"), text_color=TEXT, anchor="w", justify="left", wraplength=620
        )
        self.title_label.grid(row=1, column=1, sticky="we", padx=(0, 16), pady=(8, 4))

        row = ctk.CTkFrame(self.preview, fg_color="transparent")
        row.grid(row=2, column=1, sticky="we", padx=(0, 16), pady=(6, 0))
        self.mode_seg = ctk.CTkSegmentedButton(
            row, values=MODES, command=self._on_mode_change, font=_font(12, "bold"), height=34,
            selected_color=ACCENT, selected_hover_color=ACCENT_HOVER, unselected_color=CARD_2,
            unselected_hover_color=BORDER, fg_color=CARD_2,
        )
        self.mode_seg.pack(side="left")
        self.quality_menu = ctk.CTkOptionMenu(
            row, values=["-"], width=210, height=34, font=_font(12), fg_color=CARD_2,
            button_color=BORDER, button_hover_color=ACCENT, dropdown_font=_font(12),
        )
        self.quality_menu.pack(side="left", padx=10)

        self.download_btn = ctk.CTkButton(
            self.preview, text="↓   Download", height=42, width=200, corner_radius=10, font=_font(14, "bold"),
            fg_color=SUCCESS, hover_color=SUCCESS_HOVER, command=self.start_download,
        )
        self.download_btn.grid(row=3, column=1, sticky="w", pady=(12, 16))

    def _build_queue(self) -> None:
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=3, column=0, sticky="we", padx=26, pady=(12, 4))
        ctk.CTkLabel(head, text="Antrian Download", font=_font(15, "bold"), text_color=TEXT).pack(side="left")
        self.queue_count = ctk.CTkLabel(head, text="", font=_font(12), text_color=MUTED)
        self.queue_count.pack(side="left", padx=10)
        ctk.CTkButton(
            head, text="Bersihkan yang selesai", width=150, height=28, font=_font(12), fg_color=CARD,
            hover_color=BORDER, border_width=1, border_color=BORDER, command=self.clear_finished,
        ).pack(side="right")

        self.queue_frame = ctk.CTkScrollableFrame(
            self, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER,
            scrollbar_button_color=BORDER, scrollbar_button_hover_color=MUTED,
        )
        self.queue_frame.grid(row=4, column=0, sticky="nsew", padx=24, pady=(0, 8))
        self.queue_empty = ctk.CTkLabel(
            self.queue_frame, text="Belum ada download. File yang Anda unduh akan muncul di sini.",
            font=_font(12), text_color=MUTED,
        )
        self.queue_empty.pack(pady=30)
        self._card_order: list[JobCard] = []

    def _build_footer(self) -> None:
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=5, column=0, sticky="we", padx=24, pady=(0, 14))
        foot.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(foot, text="Simpan ke:", font=_font(12), text_color=MUTED).grid(row=0, column=0, padx=(2, 6))
        self.folder_label = ctk.CTkLabel(foot, text="", font=_font(12, "bold"), text_color=TEXT, anchor="w")
        self.folder_label.grid(row=0, column=1, sticky="we")
        self._refresh_folder_label()

        for col, (text, cmd) in enumerate(
            [("Ganti folder", self.choose_folder), ("Buka folder", lambda: self.open_output_folder())], start=2
        ):
            ctk.CTkButton(
                foot, text=text, width=104, height=28, font=_font(12), fg_color=CARD, hover_color=BORDER,
                border_width=1, border_color=BORDER, command=cmd,
            ).grid(row=0, column=col, padx=3)

        self.status_label = ctk.CTkLabel(foot, text="Siap.", font=_font(11), text_color=MUTED, anchor="w")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=2, pady=(6, 0))

        right = ctk.CTkFrame(foot, fg_color="transparent")
        right.grid(row=1, column=2, columnspan=2, sticky="e", pady=(6, 0))
        self.engine_label = ctk.CTkLabel(
            right, text=f"yt-dlp {core.yt_dlp.version.__version__}  •  FFmpeg: memeriksa…",
            font=_font(11), text_color=MUTED,
        )
        self.engine_label.pack(side="left", padx=6)
        self.update_btn = ctk.CTkButton(
            right, text="Update engine", width=104, height=24, font=_font(11), fg_color=CARD,
            hover_color=BORDER, border_width=1, border_color=BORDER, command=self.update_engine,
        )
        self.update_btn.pack(side="left")

    # ------------------------------------------------------------ helpers #
    def _set_status(self, text: str, color: str = MUTED) -> None:
        self.status_label.configure(text=text, text_color=color)

    def _refresh_folder_label(self) -> None:
        self.folder_label.configure(text=_shorten(self.settings.get("output_dir"), 80))

    def _refresh_queue_count(self) -> None:
        active = sum(1 for c in self.cards.values() if c.job.state in ("queued", "starting", "downloading", "processing"))
        total = len(self.cards)
        self.queue_count.configure(text=f"{active} aktif  •  {total} total" if total else "")
        if total:
            self.queue_empty.pack_forget()
        else:
            self.queue_empty.pack(pady=30)

    def _init_ffmpeg(self) -> None:
        path = core.find_ffmpeg()
        self.ui_queue.put(("ffmpeg", path))

    # ------------------------------------------------------------ actions #
    def paste_url(self) -> None:
        try:
            text = self.clipboard_get()
        except Exception:
            text = ""
        url = core.normalize_url(text)
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url or text.strip())
        if url:
            self.analyze()

    def analyze(self) -> None:
        if self._analyzing:
            return
        url = core.normalize_url(self.url_entry.get())
        if not url:
            self._set_status("Link tidak valid. Tempel link video yang benar (diawali https://).", DANGER)
            self.url_entry.configure(border_color=DANGER)
            self.after(1500, lambda: self.url_entry.configure(border_color=BORDER))
            return
        self._analyzing = True
        self.analyze_btn.configure(state="disabled", text="Memproses…")
        self.analyze_bar.grid()
        self.analyze_bar.start()
        self._set_status(f"Mengambil info dari {core.detect_platform(url)}…")
        threading.Thread(
            target=self._analyze_worker,
            args=(url, self.cookies_menu.get(), self.playlist_var.get()),
            daemon=True,
        ).start()

    def _analyze_worker(self, url: str, cookies: str, playlist: bool) -> None:
        try:
            info = core.fetch_info(url, cookies, playlist)
            thumb = core.fetch_thumbnail(info.thumbnail)
            self.ui_queue.put(("info_ok", info, thumb))
        except Exception as exc:  # noqa: BLE001
            self.ui_queue.put(("info_err", core.clean_error(exc)))

    def _analysis_finished(self) -> None:
        self._analyzing = False
        self.analyze_btn.configure(state="normal", text="Mulai  →")
        self.analyze_bar.stop()
        self.analyze_bar.grid_remove()

    def _show_info(self, info: core.MediaInfo, thumb: Optional[bytes]) -> None:
        self.current_info = info
        self.empty_card.grid_remove()
        self.preview.grid(row=0, column=0, sticky="we")

        image = None
        if thumb:
            try:
                image = _fit_cover(Image.open(io.BytesIO(thumb)), 512, 288)
            except Exception:
                image = None
        self._thumb_image = ctk.CTkImage(image, size=(256, 144)) if image else self._placeholder
        self.thumb_label.configure(image=self._thumb_image)

        self.platform_badge.configure(text=info.platform)
        meta = []
        if info.is_playlist:
            meta.append(f"Playlist  •  {info.entry_count} item")
        if info.uploader:
            meta.append(_shorten(info.uploader, 40))
        if info.duration:
            meta.append(core.fmt_duration(info.duration))
        self.meta_label.configure(text="  •  ".join(meta))
        self.title_label.configure(text=_shorten(info.title, 160))

        mode = self.settings.get("last_mode") if info.has_video else "Audio MP3"
        if mode not in MODES:
            mode = MODES[0]
        self.mode_seg.set(mode)
        self._on_mode_change(mode)
        self._set_status("Info berhasil diambil. Pilih format lalu klik Download.", SUCCESS)

    def _on_mode_change(self, mode: str) -> None:
        info = self.current_info
        self._quality_map = {}
        if mode == "Video MP4":
            self._quality_map["Terbaik (otomatis)"] = None
            if info:
                for h in info.heights:
                    tag = _quality_tag(h)
                    label = f"{h}p" + (f"  {tag}" if tag else "")
                    size = info.sizes.get(h)
                    if size:
                        label += f"   ≈ {core.human_size(size)}"
                    self._quality_map[label] = h
        elif mode == "Audio MP3":
            for br in core.AUDIO_BITRATES:
                label = f"{br} kbps" + ("  (terbaik)" if br == "320" else "")
                self._quality_map[label] = int(br)
        else:
            size = f"   ≈ {core.human_size(info.audio_size)}" if info and info.audio_size else ""
            self._quality_map[f"Kualitas asli{size}"] = None
        values = list(self._quality_map)
        self.quality_menu.configure(values=values)
        self.quality_menu.set(values[0])
        if info:
            self.settings.set("last_mode", mode)

    def start_download(self) -> None:
        info = self.current_info
        if not info:
            return
        mode_label = self.mode_seg.get()
        mode = MODE_KEYS.get(mode_label, "video")
        quality = self._quality_map.get(self.quality_menu.get())
        if mode != "video" and not core.find_ffmpeg():
            messagebox.showerror(APP_NAME, "FFmpeg tidak ditemukan, konversi audio tidak dapat dilakukan.")
            return
        out_dir = self.settings.get("output_dir")
        job = core.DownloadJob(
            url=info.url,
            title=info.title,
            mode=mode,
            quality=quality,
            out_dir=out_dir,
            playlist=info.is_playlist,
            cookies_browser=self.cookies_menu.get(),
            callback=lambda j, d: self.ui_queue.put(("job", j.id, d)),
            platform=info.platform,
        )
        self.submit_job(job)
        self._set_status(f"Ditambahkan ke antrian: {_shorten(info.title, 60)}")

    def submit_job(self, job: core.DownloadJob) -> None:
        card = JobCard(self.queue_frame, self, job)
        if self._card_order:
            card.pack(fill="x", padx=6, pady=5, before=self._card_order[0])
        else:
            card.pack(fill="x", padx=6, pady=5)
        self._card_order.insert(0, card)
        self.cards[job.id] = card
        self.executor.submit(job.run)
        self._refresh_queue_count()

    def remove_card(self, card: JobCard) -> None:
        card.job.cancel()
        self.cards.pop(card.job.id, None)
        if card in self._card_order:
            self._card_order.remove(card)
        card.destroy()
        self._refresh_queue_count()

    def clear_finished(self) -> None:
        for card in list(self.cards.values()):
            if card.job.state in ("done", "error", "cancelled"):
                self.remove_card(card)

    def choose_folder(self) -> None:
        path = filedialog.askdirectory(initialdir=self.settings.get("output_dir"), title="Pilih folder penyimpanan")
        if path:
            self.settings.set("output_dir", os.path.normpath(path))
            self._refresh_folder_label()

    def open_output_folder(self, path: Optional[str] = None) -> None:
        path = path or self.settings.get("output_dir")
        os.makedirs(path, exist_ok=True)
        os.startfile(path)  # type: ignore[attr-defined]

    def update_engine(self) -> None:
        if getattr(sys, "frozen", False):
            messagebox.showinfo(
                APP_NAME,
                "Versi .exe tidak bisa memperbarui engine secara otomatis.\n\n"
                "Jalankan build.bat lagi dari source code untuk mendapatkan yt-dlp terbaru.",
            )
            return
        self.update_btn.configure(state="disabled", text="Mengupdate…")
        self._set_status("Memperbarui yt-dlp…")

        def work() -> None:
            try:
                res = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-U", "yt-dlp[default]"],
                    capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=300,
                )
                ok = res.returncode == 0
                msg = "yt-dlp berhasil diperbarui. Tutup & buka kembali aplikasi untuk menerapkan." if ok else res.stderr[-400:]
            except Exception as exc:  # noqa: BLE001
                ok, msg = False, str(exc)
            self.ui_queue.put(("update_done", ok, msg))

        threading.Thread(target=work, daemon=True).start()

    # -------------------------------------------------------- event loop #
    def _poll_queue(self) -> None:
        try:
            while True:
                msg = self.ui_queue.get_nowait()
                kind = msg[0]
                if kind == "job":
                    card = self.cards.get(msg[1])
                    if card:
                        card.update_state(msg[2])
                        state = msg[2].get("state")
                        if state in ("done", "error", "cancelled", "starting"):
                            self._refresh_queue_count()
                        if state == "done":
                            self._set_status(f"Selesai: {_shorten(card.job.title, 70)}", SUCCESS)
                        elif state == "error":
                            self._set_status("Download gagal — lihat detail di antrian.", DANGER)
                elif kind == "info_ok":
                    self._analysis_finished()
                    self._show_info(msg[1], msg[2])
                elif kind == "info_err":
                    self._analysis_finished()
                    self._set_status("Gagal mengambil info.", DANGER)
                    messagebox.showerror(APP_NAME, msg[1])
                elif kind == "ffmpeg":
                    status = "siap" if msg[1] else "tidak ditemukan"
                    self.engine_label.configure(
                        text=f"yt-dlp {core.yt_dlp.version.__version__}  •  FFmpeg: {status}"
                    )
                elif kind == "update_done":
                    self.update_btn.configure(state="normal", text="Update engine")
                    self._set_status("Update selesai." if msg[1] else "Update gagal.", SUCCESS if msg[1] else DANGER)
                    (messagebox.showinfo if msg[1] else messagebox.showerror)(APP_NAME, msg[2])
        except queue.Empty:
            pass
        self.after(80, self._poll_queue)

    def open_mobile_modal(self) -> None:
        if self._web_server is None:
            try:
                self._web_server = web.start_server(self._web_port)
                threading.Thread(target=self._web_server.serve_forever, daemon=True).start()
            except Exception as e:
                messagebox.showerror(APP_NAME, f"Gagal memulai web server:\n{e}")
                return

        ip = web.get_local_ip()
        mobile_url = f"http://{ip}:{self._web_port}"

        win = ctk.CTkToplevel(self)
        win.title("Ayeraa Save Mobile")
        win.geometry("520x420")
        win.resizable(False, False)
        win.configure(fg_color=BG)
        win.transient(self)
        win.grab_set()

        pad = ctk.CTkFrame(win, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(pad, text="📱 Buka Ayeraa Save di HP Android / iOS", font=_font(18, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(
            pad, text="Pastikan HP Anda terhubung ke Wi-Fi yang sama dengan PC ini.",
            font=_font(12), text_color=MUTED
        ).pack(anchor="w", pady=(4, 16))

        box = ctk.CTkFrame(pad, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)
        box.pack(fill="x", pady=(0, 14), ipady=8)
        
        ctk.CTkLabel(box, text="Alamat Web di Browser HP:", font=_font(11), text_color=MUTED).pack(pady=(6, 2))
        url_label = ctk.CTkEntry(box, font=_font(15, "bold"), justify="center", fg_color=BG, border_color=ACCENT, height=40)
        url_label.insert(0, mobile_url)
        url_label.configure(state="readonly")
        url_label.pack(fill="x", padx=16, pady=4)

        btn_row = ctk.CTkFrame(box, fg_color="transparent")
        btn_row.pack(pady=(6, 8))

        def copy_url():
            self.clipboard_clear()
            self.clipboard_append(mobile_url)
            btn_copy.configure(text="✓ Tersalin!")
            self.after(2000, lambda: btn_copy.configure(text="Salin Alamat"))

        btn_copy = ctk.CTkButton(btn_row, text="Salin Alamat", width=120, height=32, font=_font(12, "bold"), command=copy_url)
        btn_copy.pack(side="left", padx=4)

        import webbrowser
        ctk.CTkButton(
            btn_row, text="Buka di PC", width=120, height=32, font=_font(12), fg_color=CARD_2, hover_color=BORDER,
            command=lambda: webbrowser.open(mobile_url)
        ).pack(side="left", padx=4)

        apk_box = ctk.CTkFrame(pad, fg_color=CARD_2, corner_radius=10, border_width=1, border_color=BORDER)
        apk_box.pack(fill="x", pady=6, padx=2)
        ctk.CTkLabel(
            apk_box,
            text="💡 Ingin pasang aplikasi .APK langsung di Android tanpa buka laptop?\n"
                 "Salin file dari folder 'android/' (Ayeraa Save APK) ke HP Anda.",
            font=_font(11), text_color=MUTED, justify="left"
        ).pack(padx=12, pady=10)

        ctk.CTkButton(pad, text="Tutup", width=100, height=34, font=_font(12), fg_color=BORDER, hover_color=MUTED, command=win.destroy).pack(pady=(12, 0))

    def _on_close(self) -> None:
        active = [c for c in self.cards.values() if c.job.state in ("queued", "starting", "downloading", "processing")]
        if active and not messagebox.askyesno(
            APP_NAME, f"Masih ada {len(active)} download berjalan. Batalkan dan keluar?"
        ):
            return
        for c in self.cards.values():
            c.job.cancel()
        if self._web_server:
            try:
                self._web_server.shutdown()
            except Exception:
                pass
        if self._browser_process and self._browser_process.poll() is None:
            try:
                self._browser_process.terminate()
            except Exception:
                pass
        if hasattr(self, "_ipc_server") and self._ipc_server:
            try:
                self._ipc_server.stop()
            except Exception:
                pass
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()

    # ----------------------------------------------------------- Side Browser #
    def toggle_side_browser(self) -> None:
        """Fitur rahasia (Alt+B): Buka browser modern Chromium (Edge WebView2)."""
        if self._browser_process and self._browser_process.poll() is None:
            return

        cmd = [sys.executable]
        if not getattr(sys, "frozen", False):
            cmd.append(sys.argv[0] if sys.argv else "main.py")
        cmd.extend(["--browser", "--ipc-port", str(self._ipc_port)])

        try:
            self._browser_process = subprocess.Popen(
                cmd,
                creationflags=CREATE_NO_WINDOW if getattr(sys, "frozen", False) else 0,
            )
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Gagal membuka browser internal:\n{e}")

    def _on_ipc_grab_url(self, url: str) -> None:
        """Dipanggil dari IPC server saat tombol 'Ambil Link' diklik di browser."""
        self.after(0, lambda: self._apply_grabbed_url(url))

    def _apply_grabbed_url(self, url: str) -> None:
        clean = (url or "").strip()
        if not clean:
            return

        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, clean)

        try:
            self.clipboard_clear()
            self.clipboard_append(clean)
            self.update()
        except Exception:
            pass

        self.analyze()

        try:
            self.deiconify()
            self.attributes("-topmost", True)
            self.attributes("-topmost", False)
            self.lift()
            self.focus_force()
        except Exception:
            pass

