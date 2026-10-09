"""Inti pengunduh: analisis link & proses download memakai yt-dlp."""
from __future__ import annotations

import itertools
import os
import re
import shutil
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import yt_dlp
from yt_dlp.utils import DownloadCancelled, DownloadError

from .config import app_data_dir

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
URL_RE = re.compile(r"(https?://[^\s<>\"']+)", re.IGNORECASE)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)

PLATFORMS = [
    ("music.youtube.com", "YouTube Music"),
    ("youtube.com", "YouTube"),
    ("youtu.be", "YouTube"),
    ("tiktok.com", "TikTok"),
    ("instagram.com", "Instagram"),
    ("facebook.com", "Facebook"),
    ("fb.watch", "Facebook"),
    ("fb.com", "Facebook"),
    ("twitter.com", "X / Twitter"),
    ("x.com", "X / Twitter"),
    ("threads.net", "Threads"),
    ("threads.com", "Threads"),
    ("vimeo.com", "Vimeo"),
    ("dailymotion.com", "Dailymotion"),
    ("dai.ly", "Dailymotion"),
    ("soundcloud.com", "SoundCloud"),
    ("twitch.tv", "Twitch"),
    ("reddit.com", "Reddit"),
    ("redd.it", "Reddit"),
    ("pinterest.", "Pinterest"),
    ("pin.it", "Pinterest"),
    ("bilibili.", "Bilibili"),
    ("snapchat.com", "Snapchat"),
    ("likee.", "Likee"),
    ("bandcamp.com", "Bandcamp"),
    ("linkedin.com", "LinkedIn"),
    ("tumblr.com", "Tumblr"),
    ("vk.com", "VK"),
    ("rumble.com", "Rumble"),
    ("kick.com", "Kick"),
    ("streamable.com", "Streamable"),
    ("9gag.com", "9GAG"),
    ("imgur.com", "Imgur"),
    ("mixcloud.com", "Mixcloud"),
    ("vidio.com", "Vidio"),
]

AUDIO_BITRATES = ["320", "256", "192", "128"]

_ids = itertools.count(1)


# --------------------------------------------------------------------------- #
# Utilitas
# --------------------------------------------------------------------------- #
def normalize_url(text: str) -> Optional[str]:
    """Ambil URL valid dari teks yang ditempel pengguna."""
    text = (text or "").strip()
    if not text:
        return None
    match = URL_RE.search(text)
    if match:
        return match.group(1).rstrip(".,);]")
    # Link tanpa skema, misal "youtu.be/xxxx"
    if re.match(r"^[\w.-]+\.[a-z]{2,}(/\S*)?$", text, re.IGNORECASE):
        return "https://" + text
    return None


def detect_platform(url: str, fallback: str | None = None) -> str:
    host = re.sub(r"^https?://", "", url or "", flags=re.IGNORECASE).split("/")[0].lower()
    for key, name in PLATFORMS:
        if key in host:
            return name
    if fallback:
        return fallback
    host = host.removeprefix("www.").removeprefix("m.")
    return host or "Web"


def clean_error(err: BaseException | str) -> str:
    msg = ANSI_RE.sub("", str(err)).strip()
    msg = re.sub(r"^(ERROR:\s*)+", "", msg)
    msg = re.sub(r"^\[[\w:]+\]\s*[\w-]+:\s*", "", msg)
    low = msg.lower()
    hint = ""
    if "unsupported url" in low:
        return "Link tidak didukung. Pastikan link mengarah langsung ke video/postingan."
    if any(k in low for k in ("login", "sign in", "cookies", "rate-limit", "private", "authentication")):
        hint = "\n\nTips: Pilih browser di opsi 'Cookies' (browser tempat Anda login ke situs tersebut), lalu coba lagi."
    elif "ffmpeg" in low:
        hint = "\n\nFFmpeg tidak ditemukan. Jalankan ulang aplikasi atau install FFmpeg."
    elif "getaddrinfo" in low or "timed out" in low or "connection" in low:
        hint = "\n\nPeriksa koneksi internet Anda."
    if len(msg) > 400:
        msg = msg[:400] + "..."
    return (msg or "Terjadi kesalahan tidak diketahui.") + hint


def human_size(num: Optional[float]) -> str:
    if not num:
        return "?"
    num = float(num)
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.2f} TB"


def fmt_duration(seconds: Optional[float]) -> str:
    if seconds is None:
        return ""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# --------------------------------------------------------------------------- #
# FFmpeg & JavaScript runtime
# --------------------------------------------------------------------------- #
_ffmpeg_lock = threading.Lock()
_ffmpeg_path: Optional[str] = None
_ffmpeg_checked = False


def find_ffmpeg() -> Optional[str]:
    """Cari FFmpeg di PATH; jika tidak ada pakai binary bawaan imageio-ffmpeg."""
    global _ffmpeg_path, _ffmpeg_checked
    with _ffmpeg_lock:
        if _ffmpeg_checked:
            return _ffmpeg_path
        _ffmpeg_checked = True
        found = shutil.which("ffmpeg")
        if found:
            _ffmpeg_path = found
            return found
        try:
            import imageio_ffmpeg

            src = Path(imageio_ffmpeg.get_ffmpeg_exe())
        except Exception:
            return None
        # Salin sebagai "ffmpeg.exe" agar yt-dlp mengenalinya dengan pasti.
        dest = app_data_dir() / "bin" / "ffmpeg.exe"
        try:
            if not dest.exists() or dest.stat().st_size != src.stat().st_size:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
            _ffmpeg_path = str(dest)
        except Exception:
            _ffmpeg_path = str(src)
        return _ffmpeg_path


def _bundled_dirs() -> list[Path]:
    """Folder tempat JS runtime portable bisa diletakkan (di samping .exe / folder project)."""
    import sys

    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent
    return [base, base / "bin"]


def _js_runtimes() -> Optional[dict]:
    """YouTube butuh JS runtime (deno/node/bun) untuk kualitas penuh."""
    runtimes = {}
    for name in ("deno", "node", "bun"):
        path = next(
            (str(d / f"{name}.exe") for d in _bundled_dirs() if (d / f"{name}.exe").is_file()),
            None,
        ) or shutil.which(name)
        if path:
            runtimes[name] = {"path": path}
    return runtimes or None


class _SilentLogger:
    """Logger agar yt-dlp tidak menulis ke stdout (aman untuk mode .exe tanpa konsol)."""

    def __init__(self) -> None:
        self.warnings: list[str] = []

    def debug(self, msg: str) -> None:
        pass

    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        self.warnings.append(ANSI_RE.sub("", msg))

    def error(self, msg: str) -> None:
        pass


def _base_opts(cookies_browser: Optional[str]) -> dict:
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": _SilentLogger(),
        "windowsfilenames": True,
        "retries": 5,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 4,
        "socket_timeout": 30,
        "extract_flat": "in_playlist",
    }
    runtimes = _js_runtimes()
    if runtimes:
        opts["js_runtimes"] = runtimes
    if cookies_browser and cookies_browser.lower() not in ("", "tidak ada", "none"):
        opts["cookiesfrombrowser"] = (cookies_browser.lower(),)
    return opts


# --------------------------------------------------------------------------- #
# Analisis link
# --------------------------------------------------------------------------- #
@dataclass
class MediaInfo:
    url: str
    title: str
    uploader: str
    duration: Optional[float]
    thumbnail: Optional[str]
    platform: str
    is_playlist: bool = False
    entry_count: int = 0
    heights: list[int] = field(default_factory=list)
    sizes: dict[int, int] = field(default_factory=dict)
    audio_size: Optional[int] = None
    has_video: bool = True


def _fsize(fmt: dict) -> Optional[int]:
    return fmt.get("filesize") or fmt.get("filesize_approx")


def _pick_thumbnail(info: dict) -> Optional[str]:
    thumbs = info.get("thumbnails") or []
    # Pilih thumbnail berformat jpg/png terbesar (lebih aman untuk Pillow)
    best = None
    for t in thumbs:
        url = t.get("url")
        if not url:
            continue
        score = (t.get("preference") or 0, (t.get("width") or 0) * (t.get("height") or 0))
        if best is None or score >= best[0]:
            best = (score, url)
    return info.get("thumbnail") or (best[1] if best else None)


def fetch_info(url: str, cookies_browser: Optional[str] = None, allow_playlist: bool = False) -> MediaInfo:
    opts = _base_opts(cookies_browser)
    opts.update({"skip_download": True, "noplaylist": not allow_playlist})
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info:
        raise DownloadError("Tidak ada media yang ditemukan pada link ini.")

    platform = detect_platform(url, info.get("extractor_key"))
    is_playlist = info.get("_type") == "playlist" or "entries" in info

    if is_playlist:
        entries = [e for e in (info.get("entries") or []) if e]
        thumb = _pick_thumbnail(info)
        if not thumb and entries:
            thumb = _pick_thumbnail(entries[0])
        # Postingan dengan 1 video (mis. sebagian tweet/IG) -> perlakukan sebagai video tunggal
        if len(entries) == 1 and entries[0].get("formats"):
            info = entries[0]
            is_playlist = False
        else:
            return MediaInfo(
                url=url,
                title=info.get("title") or "Playlist",
                uploader=info.get("uploader") or info.get("channel") or "",
                duration=None,
                thumbnail=thumb,
                platform=platform,
                is_playlist=True,
                entry_count=info.get("playlist_count") or len(entries),
                heights=[2160, 1440, 1080, 720, 480, 360],
                has_video=True,
            )

    formats = info.get("formats") or []
    audio_formats = [
        f for f in formats if f.get("vcodec") == "none" and f.get("acodec") not in (None, "none")
    ]
    best_audio = max(audio_formats, key=lambda f: f.get("abr") or 0, default=None)
    audio_size = _fsize(best_audio) if best_audio else None

    sizes: dict[int, int] = {}
    heights: set[int] = set()
    for f in formats:
        if f.get("vcodec") == "none":
            continue
        h = f.get("height")
        if not h:
            continue
        # Normalisasi video portrait (TikTok/Reels): gunakan sisi terpendek
        w = f.get("width")
        res = min(h, w) if w else h
        heights.add(res)
        size = _fsize(f)
        if size:
            if f.get("acodec") == "none" and audio_size:
                size += audio_size
            sizes[res] = max(sizes.get(res, 0), size)
    if not heights and info.get("height"):
        h, w = info["height"], info.get("width")
        heights.add(min(h, w) if w else h)

    has_video = (not formats) or any(f.get("vcodec") != "none" for f in formats)
    if not formats and info.get("vcodec") == "none":
        has_video = False

    return MediaInfo(
        url=url,
        title=info.get("title") or info.get("id") or "Tanpa judul",
        uploader=info.get("uploader") or info.get("channel") or info.get("creator") or "",
        duration=info.get("duration"),
        thumbnail=_pick_thumbnail(info),
        platform=platform,
        heights=sorted(heights, reverse=True),
        sizes=sizes,
        audio_size=audio_size,
        has_video=has_video,
    )


def fetch_thumbnail(url: Optional[str]) -> Optional[bytes]:
    if not url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Download
# --------------------------------------------------------------------------- #
class DownloadJob:
    """Satu tugas download. `callback(job, data: dict)` dipanggil dari thread worker."""

    def __init__(
        self,
        url: str,
        title: str,
        mode: str,  # "video" | "mp3" | "m4a"
        quality: Optional[int],
        out_dir: str,
        playlist: bool,
        cookies_browser: Optional[str],
        callback: Callable[["DownloadJob", dict], None],
        platform: str = "",
    ) -> None:
        self.id = next(_ids)
        self.url = url
        self.title = title
        self.mode = mode
        self.quality = quality
        self.out_dir = out_dir
        self.playlist = playlist
        self.cookies_browser = cookies_browser
        self.callback = callback
        self.platform = platform
        self.cancel_event = threading.Event()
        self.filepath: Optional[str] = None
        self.state = "queued"
        self._last_emit = 0.0
        self._tmpfiles: set[str] = set()

    # -- util ------------------------------------------------------------- #
    def clone(self) -> "DownloadJob":
        return DownloadJob(
            self.url, self.title, self.mode, self.quality, self.out_dir,
            self.playlist, self.cookies_browser, self.callback, self.platform,
        )

    @property
    def label(self) -> str:
        if self.mode == "video":
            return f"MP4 {self.quality}p" if self.quality else "MP4 Terbaik"
        if self.mode == "mp3":
            return f"MP3 {self.quality or 320}kbps"
        return "M4A"

    def cancel(self) -> None:
        self.cancel_event.set()

    def _emit(self, **data) -> None:
        self.state = data.get("state", self.state)
        self.callback(self, data)

    # -- hooks ------------------------------------------------------------ #
    def _progress_hook(self, d: dict) -> None:
        if self.cancel_event.is_set():
            raise DownloadCancelled("Dibatalkan oleh pengguna")
        status = d.get("status")
        if d.get("tmpfilename"):
            self._tmpfiles.add(d["tmpfilename"])
        info = d.get("info_dict") or {}
        item = None
        if self.playlist and info.get("playlist_index"):
            item = (info.get("playlist_index"), info.get("n_entries") or info.get("playlist_count"))

        if status == "downloading":
            now = time.monotonic()
            if now - self._last_emit < 0.15:
                return
            self._last_emit = now
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            done = d.get("downloaded_bytes") or 0
            frac = (done / total) if total else None
            if frac is None and d.get("fragment_count"):
                frac = (d.get("fragment_index") or 0) / d["fragment_count"]
            self._emit(
                state="downloading",
                progress=min(frac, 1.0) if frac is not None else None,
                downloaded=done,
                total=total,
                speed=d.get("speed"),
                eta=d.get("eta"),
                item=item,
            )
        elif status == "finished":
            if d.get("filename"):
                self.filepath = d["filename"]
            self._emit(state="downloading", progress=1.0, item=item)

    def _pp_hook(self, d: dict) -> None:
        if self.cancel_event.is_set():
            raise DownloadCancelled("Dibatalkan oleh pengguna")
        status = d.get("status")
        pp = d.get("postprocessor", "")
        if status == "started":
            text = {
                "Merger": "Menggabungkan video & audio...",
                "ExtractAudio": "Mengonversi audio...",
                "FFmpegExtractAudio": "Mengonversi audio...",
                "FFmpegMetadata": "Menulis metadata...",
                "Metadata": "Menulis metadata...",
            }.get(pp, "Memproses...")
            self._emit(state="processing", text=text)
        elif status == "finished":
            path = (d.get("info_dict") or {}).get("filepath")
            if path:
                self.filepath = path

    # -- main ------------------------------------------------------------- #
    def _build_opts(self, ffmpeg: Optional[str]) -> dict:
        opts = _base_opts(self.cookies_browser)
        opts.pop("extract_flat", None)
        opts.update(
            {
                "noplaylist": not self.playlist,
                "paths": {"home": self.out_dir, "temp": self.out_dir},
                "progress_hooks": [self._progress_hook],
                "postprocessor_hooks": [self._pp_hook],
                "overwrites": False,
                "continuedl": True,
                "ignoreerrors": "only_download" if self.playlist else False,
            }
        )
        if self.playlist:
            opts["outtmpl"] = "%(playlist_title,playlist_id)s/%(playlist_index)03d - %(title).150B.%(ext)s"
        else:
            opts["outtmpl"] = "%(title).150B.%(ext)s"
        if ffmpeg:
            opts["ffmpeg_location"] = ffmpeg

        if self.mode == "video":
            res = f"res:{self.quality}" if self.quality else "res"
            # Utamakan H.264/AAC (MP4) agar bisa diputar di semua pemutar Windows
            opts["format_sort"] = [res, "vcodec:h264", "ext:mp4:m4a"]
            if ffmpeg:
                opts["format"] = "bv*+ba/b"
                opts["merge_output_format"] = "mp4"
            else:
                opts["format"] = "b[ext=mp4]/b"
        else:
            if not ffmpeg:
                raise DownloadError("FFmpeg diperlukan untuk konversi audio.")
            codec = "mp3" if self.mode == "mp3" else "m4a"
            opts["format"] = "ba[ext=m4a]/ba/b" if codec == "m4a" else "ba/b"
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": codec,
                    "preferredquality": str(self.quality or 320) if codec == "mp3" else "0",
                },
                {"key": "FFmpegMetadata", "add_metadata": True},
            ]
        return opts

    def _cleanup_partials(self) -> None:
        for tmp in self._tmpfiles:
            for path in (tmp, tmp + ".ytdl"):
                try:
                    if path.endswith((".part", ".ytdl")) and os.path.exists(path):
                        os.remove(path)
                except OSError:
                    pass

    def run(self) -> None:
        if self.cancel_event.is_set():
            self._emit(state="cancelled")
            return
        self._emit(state="starting")
        try:
            os.makedirs(self.out_dir, exist_ok=True)
            opts = self._build_opts(find_ffmpeg())
            with yt_dlp.YoutubeDL(opts) as ydl:
                retcode = ydl.download([self.url])
            if self.cancel_event.is_set():
                raise DownloadCancelled()
            if retcode and not self.playlist:
                raise DownloadError("Download gagal.")
            self._emit(state="done", filepath=self.filepath)
        except DownloadCancelled:
            self._cleanup_partials()
            self._emit(state="cancelled")
        except Exception as exc:  # noqa: BLE001
            if self.cancel_event.is_set():
                self._cleanup_partials()
                self._emit(state="cancelled")
            else:
                self._emit(state="error", error=clean_error(exc))
