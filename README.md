# Ayeraa Save Downloader

Aplikasi Windows untuk mengunduh video & audio dari **semua platform** — mirip y2mate, tapi tanpa iklan dan berjalan langsung di PC Anda.

Didukung: **YouTube, YouTube Music, TikTok, Instagram, Facebook, X/Twitter, Threads, Vimeo, Dailymotion, SoundCloud, Twitch, Reddit, Pinterest, Bilibili**, dan 1000+ situs lain (semua situs yang didukung [yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)).

## Fitur
- Tempel link → **Mulai** → pilih format → **Download**
- **Video MP4** sampai 4K (estimasi ukuran file untuk tiap resolusi)
- **Audio MP3** (320/256/192/128 kbps) dan **M4A** kualitas asli
- Preview thumbnail, judul, uploader, durasi, platform
- **Antrian download** paralel dengan progress, kecepatan, sisa waktu, tombol batal & ulangi
- Download **playlist** utuh (YouTube, SoundCloud, dll.)
- **Cookies dari browser** untuk konten yang butuh login (Instagram, Facebook, video privat)
- FFmpeg **sudah termasuk** (tidak perlu install terpisah)
- **Dukungan Android**:
  - **APK Siap Pakai di HP**: File installer di folder `android/` (Ayeraa Save APK).
  - **Mode Web Server di HP**: Klik "📱 Buka di HP" atau jalankan `run_web.bat` untuk membuka UI mobile lewat browser HP di Wi-Fi yang sama!
- Tombol **Update engine** agar tetap kompatibel saat situs berubah

## Cara menjalankan (dari source)
Butuh Python 3.10+.

```bat
run.bat
```
atau manual:
```bat
pip install -r requirements.txt
python main.py
```

## Membuat file .exe (portable)
```bat
build.bat
```
Hasil: `dist\Ayeraa Save Downloader.exe` — satu file, bisa disalin ke PC lain tanpa Python.

## Tips
- **YouTube kualitas tinggi** membutuhkan JavaScript runtime. Aplikasi otomatis memakai **Node.js / Deno / Bun** jika terpasang.
- **Instagram/Facebook gagal?** Login ke situs tersebut di browser (disarankan **Firefox**), lalu pilih browser itu di opsi *Cookies dari browser*.
  Chrome/Edge versi baru mengenkripsi cookies — tutup browser tersebut dulu jika gagal.
- Jika suatu situs tiba-tiba error, klik **Update engine** (mode source) atau build ulang .exe.

## Struktur
```
main.py              entry point
allsave/core.py      engine (yt-dlp): analisis link, pilih format, download, progress
allsave/ui.py        antarmuka (customtkinter)
allsave/config.py    pengaturan (%APPDATA%\AllSaveDownloader\settings.json)
allsave/branding.py  logo/ikon
tools/make_icon.py   membuat assets/icon.ico
```

> Gunakan secara bertanggung jawab. Hanya unduh konten yang Anda miliki haknya atau diizinkan oleh pemiliknya.
