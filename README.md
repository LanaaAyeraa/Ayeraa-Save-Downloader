# Ayeraa Save Downloader & Ayera Downloader Pro v2.0

Aplikasi download manager serbaguna untuk Windows & Android:
- **Ayera Downloader Pro v2.0 (Rust IDM Accelerator Core)**: Akselerator download multi-thread segmented berkecepatan tinggi mirip Internet Download Manager (IDM) dengan desain visual hangat **Claude Aesthetic**, context menu klik kanan **Open File Location**, routing kategori otomatis, dan limiter kecepatan.
- **Ayeraa Save Downloader (Multi-Platform Extractor)**: Unduh video & audio dari YouTube, TikTok, Instagram, Facebook, X/Twitter, dan 1000+ situs lain tanpa iklan.

---

## 🚀 Ayera Downloader Pro v2.0 (Rust IDM Edition)

Fitur unggulan core desktop Rust yang terinspirasi dari arsitektur IDM:
- **Multi-Part Segmented Acceleration**: Memecah unduhan file besar menjadi 8 koneksi paralel simultan (`Range: bytes=X-Y`) untuk memaksimalkan bandwidth.
- **Claude Aesthetic UI**: Tampilan modern Warm Charcoal (`#1A1918`), Card Surface (`#242321`), Terracotta Accent (`#CC5A37`), dan tipografi clean editorial.
- **Context Menu Klik Kanan**:
  - 📂 **Open File Location**: Buka Windows Explorer dan langsung menyorot (*highlight*) file yang diunduh (`explorer.exe /select,"<path>"`).
  - ▶ **Open File**: Langsung putar/buka file yang selesai diunduh.
  - 📋 **Copy Download Link**: Salin URL unduhan ke clipboard.
  - ⏸ **Pause / ▶ Resume**: Kontrol status unduhan individual atau serentak.
  - 🗑 **Delete Download**: Hapus item dari daftar dan disk.
- **Auto Category Routing**: Otomatis mendeteksi ekstensi dan menyortir file ke direktori khusus:
  - `Compressed/` (`.zip`, `.rar`, `.7z`, `.tar`, `.gz`)
  - `Documents/` (`.pdf`, `.doc`, `.docx`, `.epub`, `.txt`)
  - `Music/` (`.mp3`, `.wav`, `.flac`, `.aac`, `.m4a`)
  - `Programs/` (`.exe`, `.msi`, `.apk`, `.deb`)
  - `Video/` (`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`)
- **Dynamic Speed Limiter**: Batasi kecepatan download maksimum secara akurat untuk membagi bandwidth.
- **Persistent State & Queue**: Seluruh antrean tersimpan otomatis di `%APPDATA%\AyeraDownloader\state.json`.
- **Standalone Setup Installer**: File instalasi ringan tunggal (`ayera_setup.exe` / 5.6 MB) yang otomatis memasang ke `%LOCALAPPDATA%\Programs\Ayera Downloader`, membuat shortcut Desktop & Start Menu, lalu meluncurkan aplikasi.
- **Hardtested 100% Green**: Dilengkapi test suite `tests/hardtest.rs` dengan validasi range chunking, explorer path parsing, limiter math, dan mock HTTP concurrent download.

---

## 📥 Download Aplikasi (Siap Pakai)

Pilih installer sesuai kebutuhan Anda:

| Perangkat | Format | Link Download | Keterangan |
| :--- | :--- | :--- | :--- |
| **Windows** | **Pro v2.0 Setup (Rust IDM)** | [**ayera_setup.exe**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/releases/download/v2.0.0/ayera_setup.exe) (5.6 MB) | **Rekomendasi Utama!** Akselerator IDM super cepat, Claude Aesthetic, klik kanan open file location |
| **Windows** | **Pro v2.0 Portable (Rust IDM)** | [**ayera_downloader.exe**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/releases/download/v2.0.0/ayera_downloader.exe) (5.4 MB) | Versi portable tanpa install, langsung jalan |
| **Windows** | Legacy AllSave Setup | [**Ayeraa-Save-Downloader-Setup.exe**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/releases/download/v1.1.0/Ayeraa-Save-Downloader-Setup.exe) (90 MB) | Versi extractor YouTube/Medsos klasik |
| **Android** | Installer APK | [**Ayeraa-Save-Downloader.apk**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/releases/download/v1.1.0/Ayeraa-Save-Downloader.apk) (41 MB) | Material You, tanpa iklan, share link langsung |
| **Android** | APK Pro | [**Ayeraa-Save-Downloader-Pro.apk**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/releases/download/v1.1.0/Ayeraa-Save-Downloader-Pro.apk) (65 MB) | Fitur potong audio/video & batch format |
| **Android (New)** | Project Mobile shadcn/ui | [**Ayeraa-Save-Downloader-Mobile-shadcn.zip**](https://github.com/LanaaAyeraa/Ayeraa-Save-Downloader/releases/download/v1.1.0/Ayeraa-Save-Downloader-Mobile-shadcn.zip) (1 MB) | Engine Mori + UI shadcn/ui (Capacitor) |

---

## 🛠 Menjalankan & Membangun Ayera Downloader Pro (Rust)

### Menjalankan Langsung
```bat
run_desktop_rust.bat
```
Atau manual:
```bat
cargo run --release --manifest-path desktop-rust/Cargo.toml --bin ayera_downloader
```

### Menjalankan Hard Test
```bat
cargo test --manifest-path desktop-rust/Cargo.toml
```

### Membangun Release Binary & Installer
```bat
cd desktop-rust
build.bat
```
Hasil build:
- Binary: `desktop-rust\target\release\ayera_downloader.exe`
- Standalone Installer: `desktop-rust\target\release\ayera_setup.exe`

---

## Fitur Media Extractor (Legacy Core)
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
