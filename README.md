# Ayeraa Save Downloader

Aplikasi Windows untuk mengunduh video & audio dari **semua platform** — mirip y2mate, tapi tanpa iklan dan berjalan langsung di PC Anda.

Didukung: **YouTube, YouTube Music, TikTok, Instagram, Facebook, X/Twitter, Threads, Vimeo, Dailymotion, SoundCloud, Twitch, Reddit, Pinterest, Bilibili**, dan 1000+ situs lain (semua situs yang didukung [yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)).

## 📥 Download Aplikasi (Siap Pakai)

Pilih installer sesuai kebutuhan Anda:

| Perangkat | Format | Link Download | Keterangan |
| :--- | :--- | :--- | :--- |
| **Windows** | **Installer .EXE (Rekomendasi)** | [**Ayeraa-Save-Downloader-Setup.exe**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/releases/download/v1.0.0/Ayeraa-Save-Downloader-Setup.exe) (90 MB) | Tinggal klik 2x, otomatis pasang shortcut di Desktop & Start Menu |
| **Windows** | Portable ZIP | [**Ayeraa-Save-Downloader-Windows.zip**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/releases/download/v1.0.0/Ayeraa-Save-Downloader-Windows.zip) (100 MB) | Versi portable tanpa install |
| **Android** | Installer APK | [**Ayeraa-Save-Downloader.apk**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/raw/main/android/Ayeraa-Save-Downloader.apk) (41 MB) | Material You, tanpa iklan, share link langsung |
| **Android** | APK Pro | [**Ayeraa-Save-Downloader-Pro.apk**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/raw/main/android/Ayeraa-Save-Downloader-Pro.apk) (65 MB) | Fitur potong audio/video & batch format |

---

## Fitur
- Tempel link → **Mulai** → pilih format → **Download**
- **Video MP4** sampai 4K (estimasi ukuran file untuk tiap resolusi)
- **Audio MP3** (320/256/192/128 kbps) dan **M4A** kualitas asli
- Preview thumbnail, judul, uploader, durasi, platform
- **Antrian download** paralel dengan progress, kecepatan, sisa waktu, tombol batal & ulangi
- Download **playlist** utuh (YouTube, SoundCloud, dll.)
- **Cookies dari browser** untuk konten yang butuh login (Instagram, Facebook, video privat)
- FFmpeg & Deno **sudah termasuk** (tidak perlu install terpisah)
- **Dukungan Android & Mobile Modern (Mori Engine + shadcn/ui)**:
  - **Arsitektur Baru**: UI modern berbasis **shadcn/ui** (React 19 + Tailwind CSS + Lucide Icons) dengan backend client-side extractor tanpa iklan.
  - **Capacitor Android Project**: Tersedia di folder `mobile/` dengan native bridge, foreground notification, and automatic gallery media scanning.
  - **Build APK Otomatis**: Dilengkapi GitHub Actions CI (`.github/workflows/build-android.yml`) untuk build APK cloud.
  - **Jalankan Preview Web Mobile**: Klik ganda `run_mobile_web.bat` atau `cd mobile && npm run dev` untuk membuka antarmuka mobile di browser!
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

## Membuat Installer .exe
```bat
# 1. Build binary
build.bat

# 2. Compile setup installer
iscc installer.iss
```
Hasil installer: `dist-installer\Ayeraa-Save-Downloader-Setup.exe`

## Tips
- **YouTube kualitas tinggi** membutuhkan JavaScript runtime. Aplikasi otomatis memakai **Node.js / Deno / Bun** (Deno sudah disertakan di installer).
- **Instagram/Facebook gagal?** Login ke situs tersebut di browser (disarankan **Firefox**), lalu pilih browser itu di opsi *Cookies dari browser*.
  Chrome/Edge versi baru mengenkripsi cookies — tutup browser tersebut dulu jika gagal.
- Jika suatu situs tiba-tiba error, klik **Update engine** (mode source) atau build ulang .exe.

## Struktur
```
main.py              entry point
installer.iss        skrip Inno Setup untuk membuat Setup.exe
allsave/core.py      engine (yt-dlp): analisis link, pilih format, download, progress
allsave/ui.py        antarmuka desktop (customtkinter)
allsave/web.py       antarmuka web mobile & server PWA
allsave/config.py    pengaturan (%APPDATA%\AyeraaSaveDownloader\settings.json)
allsave/branding.py  logo/ikon
tools/make_icon.py   membuat assets/icon.ico
```

> Gunakan secara bertanggung jawab. Hanya unduh konten yang Anda miliki haknya atau diizinkan oleh pemiliknya.
