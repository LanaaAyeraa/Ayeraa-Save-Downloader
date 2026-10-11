# ADR 0001: Mobile Architecture with Capacitor & shadcn/ui

## Status
Accepted

## Context
The user requested an Android mobile downloader inspired by Mori (`coflyn/Mori`), styled with modern shadcn/ui components (React, Tailwind CSS, Lucide Icons) rather than the older desktop CustomTkinter look.

## Decision
- Build a client-side Vite + React application wrapped with Capacitor 7.
- Implement UI components using shadcn/ui principles (accessible, sleek dark mode theme, modular).
- Retain native bridge (`MoriMainBridge`) for raw HTTP access, direct storage file management, and foreground notification downloads.

## Consequences
- High performance, responsive layout tailored for mobile displays.
- Cross-platform codebase ready for both web preview and Android APK packaging.
