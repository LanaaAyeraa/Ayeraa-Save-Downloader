# Implementation Roadmap & Tickets: Ayeraa Mobile Downloader

## Ticket 01: Scaffold Vite + React + TypeScript + Tailwind CSS + shadcn/ui Project
- Initialize `mobile/` project directory.
- Configure `tailwind.config.js`, `postcss.config.js`, and root CSS variables for shadcn/ui dark theme.
- Install essential packages: `lucide-react`, `clsx`, `tailwind-merge`, `@capacitor/core`, `@capacitor/android`, `@capacitor/filesystem`, `@capacitor/clipboard`, `@capacitor/haptics`, `@capacitor/share`, `@capacitor/network`.

## Ticket 02: Port & Modernize Scraper Engine (TypeScript Services)
- Create `src/services/scrapers/` containing extractors for TikTok, Instagram, YouTube, Twitter/X, Spotify, Facebook, Pinterest, Douyin, Bilibili.
- Implement `httpHelper.ts` with transparent failover between Android Native Bridge (`MoriMainBridge`), `CapacitorHttp`, and browser `fetch`.
- Implement download resolver and storage manager (`src/services/downloader/`).

## Ticket 03: Build Mobile-First shadcn/ui Components & Views
- Reusable UI primitives: Button, Card, Badge, Input, Progress, Tabs, Dialog, Toast.
- Downloader view with URL auto-paste, platform detection badge, extract trigger.
- Result card with thumbnail preview, author/title info, resolution & audio selectors.
- Active progress tracker with real-time percentage and cancel button.
- History view with local persistence, share, open, and clear options.
- Settings view for download path, default server sources, and Wi-Fi preferences.

## Ticket 04: Capacitor Android Integration & GitHub Actions Workflow
- Configure `capacitor.config.ts` for Ayeraa Save Downloader (`appId: com.ayeraa.downloader`).
- Integrate Android native project with foreground download service and share intent receiver.
- Setup GitHub Actions workflow `.github/workflows/android-build.yml` for automated cloud APK compilation and releases.

## Ticket 05: In-App Seamless Auto-Update (No Reinstall Required)
- Persistent PKCS#12 signing keystore (`release.keystore`) configured in `build.gradle` for both release and debug variants.
- Android manifest permission `<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />`.
- Native installer and download methods in `MainActivity.java` (`MoriMainBridge`).
- Front-end `updaterService.ts` querying GitHub Releases API with semver resolution.
- UI updater modal (shadcn/ui Dialog + Progress) in `App.tsx` and manual update check in `SettingsView.tsx`.
