# Technical Specification: Ayeraa Save Downloader (Mobile - shadcn/ui + Capacitor)

## 1. Overview
Build a high-performance Android mobile application inspired by **Mori** (`coflyn/Mori`), completely re-architected with **shadcn/ui** (React, Tailwind CSS, Lucide Icons) and packaged with **Capacitor**. The application performs client-side media extraction and downloading across multiple platforms (TikTok, Instagram, YouTube, X/Twitter, Spotify, Facebook, Pinterest, Douyin, Bilibili, etc.) directly on the user's device without requiring an external heavy backend.

## 2. Key Architecture & Tech Stack

### 2.1 Frontend & UI Standard
- **Framework**: React 18 + Vite + TypeScript.
- **Styling**: Tailwind CSS with custom design tokens, dark mode palette, smooth gradients, and mobile-friendly touch targets.
- **Component System (shadcn/ui)**:
  - `Button`, `Input`, `Card`, `Badge`, `Progress`, `Tabs`, `Dialog`, `DropdownMenu`, `Switch`, `Toast`.
  - Iconography: `lucide-react`.
- **State Management**: React state & custom hooks for active downloads, history persistence in `localStorage` and Capacitor storage.

### 2.2 Mobile Native Runtime
- **Runtime**: Capacitor (`@capacitor/core`, `@capacitor/android`, `@capacitor/filesystem`, `@capacitor/clipboard`, `@capacitor/haptics`, `@capacitor/share`, `@capacitor/network`).
- **Android Native Bridge**:
  - `MoriMainBridge` / `AyeraaBridge` on Android WebView for unrestricted HTTP requests (`OkHttpClient`) bypassing CORS.
  - Native media scanner (`MediaScannerConnection`) ensuring downloaded videos, photos, and music immediately populate Android Gallery / Photos and Music apps.
  - Foreground download service with persistent notification during large transfers.
  - Android Share Intent Receiver (`ShareActivity`) allowing users to tap "Share to Ayeraa Save" from TikTok, Instagram, YouTube, etc.

### 2.3 Scraper & Downloader Engine
- Fully client-side extractor pipeline matching Mori's capabilities:
  - **TikTok**: Single videos (No watermark / HD), photo slide carousels, audio extraction.
  - **Instagram**: Reels, posts, carousels, stories via SnapSave and InDown.
  - **YouTube**: Video resolutions (1080p, 720p, 360p), MP3 audio conversion, and playlist track extractions.
  - **Twitter / X**: Video stream extractions (HD/SD) and photos via TVD and SaveTWT.
  - **Spotify**: Tracks, albums, and playlists resolved to high-quality audio streams.
  - **Additional Platforms**: Facebook, Pinterest, Threads, Bilibili, Douyin, RedNote/Xiaohongshu.
- Resilient retry logic, source failover, and cancelable downloads.

## 3. UI/UX Wireframe & Layout
- **Header**: Branding ("Ayeraa Save Downloader"), connection indicator, quick theme toggle, and repository/about pill.
- **Platform Pills**: Scrollable row of supported platform badges (TikTok, YouTube, IG, Spotify, X, FB, Pinterest, Douyin).
- **Extraction Input Area**:
  - URL input with integrated Clear & Auto-Paste buttons.
  - Instant Platform Badge detection on typing/pasting.
  - Primary "Extract Media" / "Download" action button with loading spinner.
- **Media Preview Card**:
  - High-res cover/thumbnail preview with duration / author pill.
  - Content title and author.
  - Format list with clear download buttons (e.g. `1080p HD`, `720p MP4`, `MP3 Audio`, `All Photos`).
- **Active Task / Progress Widget**:
  - Real-time animated progress bar with percentage, downloaded MB, and cancel trigger.
- **Tab Navigation**:
  - `Downloader`: Main scraper & download view.
  - `History`: List of past downloads with open in gallery / share / delete actions.
  - `Settings`: Download directory, auto-retry, default server sources, dark mode.
