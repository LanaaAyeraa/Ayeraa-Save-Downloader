// Download Manager Service for Ayeraa Save Downloader
// Supports Capacitor Native Filesystem, Android Foreground Service, and Browser Fallback

import { Filesystem, Directory } from "@capacitor/filesystem";
import { Haptics, ImpactStyle, NotificationType } from "@capacitor/haptics";
import { type DownloadItem } from "./scraperEngine";

export interface HistoryItem {
  id: string;
  title: string;
  type: string;
  url: string;
  localPath?: string;
  thumbnail?: string;
  platform: string;
  timestamp: number;
  size?: string;
}

export function sanitizeFilename(title: string, type: string, ext = "mp4"): string {
  const cleanTitle = (title || "Ayeraa_Media")
    .replace(/[\\/:*?"<>|#%&{}[\]@$^+=~`';,]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 60);

  const cleanType = (type || "").replace(/[^a-zA-Z0-9]/g, "_");
  const timestamp = Date.now().toString().slice(-4);
  return `Ayeraa_${cleanTitle}_${cleanType}_${timestamp}.${ext}`;
}

export function resolveExtension(type: string, url: string): string {
  const t = (type || "").toLowerCase();
  const u = (url || "").toLowerCase();
  if (t.includes("mp3") || t.includes("audio") || u.includes(".mp3")) return "mp3";
  if (t.includes("m4a") || u.includes(".m4a")) return "m4a";
  if (t.includes("photo") || t.includes("image") || u.includes(".jpg") || u.includes(".jpeg")) return "jpg";
  if (t.includes("png") || u.includes(".png")) return "png";
  if (t.includes("webp") || u.includes(".webp")) return "webp";
  return "mp4";
}

/**
 * Resolves indirect/tokenized URLs (e.g. soundloaders_resolve or spotidown_resolve)
 */
export async function resolveDirectMediaUrl(
  url: string,
  onStatusUpdate?: (msg: string) => void
): Promise<string> {
  if (url.startsWith("soundloaders_resolve:")) {
    onStatusUpdate?.("Resolving high-quality Spotify audio stream...");
    const payload = url.replace("soundloaders_resolve:", "").split("|||");
    const [data, token, base] = payload;
    try {
      const boundary = "----WebKitFormBoundary" + Math.random().toString(36).substring(2);
      const body =
        `--${boundary}\r\nContent-Disposition: form-data; name="data"\r\n\r\n${data}\r\n` +
        `--${boundary}\r\nContent-Disposition: form-data; name="base"\r\n\r\n${decodeURIComponent(base || "")}\r\n` +
        `--${boundary}\r\nContent-Disposition: form-data; name="token"\r\n\r\n${token}\r\n` +
        `--${boundary}--\r\n`;

      const res = await fetch("https://spotimate.app/action/track", {
        method: "POST",
        headers: {
          "Content-Type": `multipart/form-data; boundary=${boundary}`,
        },
        body,
      });
      const json = await res.json();
      const trackData = json?.data || json?.html || "";
      const doc = new DOMParser().parseFromString(trackData, "text/html");
      const a = doc.querySelector("a[href^='http']");
      if (a) {
        const href = a.getAttribute("href");
        if (href) return href;
      }
    } catch {
      // fallback
    }
  }

  if (url.startsWith("spotidown_resolve:")) {
    onStatusUpdate?.("Resolving track from SpotiDown servers...");
    const payload = url.replace("spotidown_resolve:", "").split("|||");
    const [serializedForm, cookie] = payload;
    try {
      const res = await fetch("https://spotidown.app/action/track", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
          Cookie: decodeURIComponent(cookie || ""),
        },
        body: serializedForm,
      });
      const json = await res.json();
      const doc = new DOMParser().parseFromString(json?.data || "", "text/html");
      const a = doc.querySelector("a[href^='http']");
      if (a) {
        const href = a.getAttribute("href");
        if (href) return href;
      }
    } catch {
      // fallback
    }
  }

  return url;
}

export async function triggerHaptic(type: "success" | "medium" | "error" = "medium") {
  try {
    if (type === "success") {
      await Haptics.notification({ type: NotificationType.Success });
    } else if (type === "error") {
      await Haptics.notification({ type: NotificationType.Error });
    } else {
      await Haptics.impact({ style: ImpactStyle.Medium });
    }
  } catch {
    // vibrate fallback
    if (navigator.vibrate) navigator.vibrate(type === "success" ? [40, 80] : 40);
  }
}

/**
 * Downloads a media item to Android storage (or triggers browser download)
 */
export async function downloadMediaItem(
  item: DownloadItem,
  mediaTitle: string,
  platform: string,
  onProgress: (percent: number, statusText: string) => void
): Promise<{ success: boolean; filename: string; path?: string; message?: string }> {
  try {
    onProgress(5, "Connecting to download stream...");
    const directUrl = await resolveDirectMediaUrl(item.url, (msg) => onProgress(15, msg));
    const ext = resolveExtension(item.type, directUrl);
    const filename = sanitizeFilename(mediaTitle, item.type, ext);

    const isAndroid = (window as any).Capacitor?.getPlatform?.() === "android";
    const bridge = (window as any).MoriMainBridge || (window as any).AyeraaBridge;

    // Start Foreground Notification Service on Android if available
    if (bridge?.startDownloadService) {
      bridge.startDownloadService(`Downloading ${mediaTitle.substring(0, 30)}...`);
    }

    onProgress(25, "Starting download...");

    let savedPath = "";

    // 1. Native Capacitor Filesystem Download
    if (isAndroid) {
      try {
        const downloadRes = await Filesystem.downloadFile({
          url: directUrl,
          path: filename,
          directory: Directory.Documents,
          progress: true,
        });

        savedPath = downloadRes.path || filename;
        onProgress(95, "Registering media in Android gallery...");

        // Scan file so it shows in Google Photos / Gallery / Music
        if (bridge?.scanMediaFile) {
          const mimeType = ext === "mp3" ? "audio/mpeg" : ext === "jpg" ? "image/jpeg" : "video/mp4";
          bridge.scanMediaFile(savedPath, mimeType);
        }
      } catch (nativeErr: any) {
        console.warn("Native download error, trying blob fallback:", nativeErr);
        // Fallback to fetch blob
        const resp = await fetch(directUrl);
        const blob = await resp.blob();
        const base64Data = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            const res = reader.result as string;
            resolve(res.split(",")[1]);
          };
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        });

        await Filesystem.writeFile({
          path: filename,
          data: base64Data,
          directory: Directory.Documents,
        });
      }
    } else {
      // 2. Web Browser Fallback
      onProgress(50, "Downloading media buffer...");
      const link = document.createElement("a");
      link.href = directUrl;
      link.download = filename;
      link.target = "_blank";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    if (bridge?.stopDownloadService) {
      bridge.stopDownloadService();
    }

    onProgress(100, "Download completed!");
    await triggerHaptic("success");

    // Add to History
    saveToHistory({
      id: Date.now().toString(),
      title: mediaTitle,
      type: item.type,
      url: directUrl,
      localPath: savedPath || filename,
      thumbnail: item.thumbnail,
      platform,
      timestamp: Date.now(),
      size: item.size,
    });

    return { success: true, filename, path: savedPath };
  } catch (err: any) {
    const bridge = (window as any).MoriMainBridge || (window as any).AyeraaBridge;
    if (bridge?.stopDownloadService) {
      bridge.stopDownloadService();
    }
    await triggerHaptic("error");
    return {
      success: false,
      filename: "",
      message: err.message || "Failed to download media file.",
    };
  }
}

// History Storage Utilities
const HISTORY_KEY = "ayeraa_download_history";

export function getHistory(): HistoryItem[] {
  try {
    const data = localStorage.getItem(HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

export function saveToHistory(item: HistoryItem) {
  try {
    const existing = getHistory();
    const updated = [item, ...existing.filter((i) => i.id !== item.id)].slice(0, 100);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  } catch {
    // ignore
  }
}

export function clearHistory() {
  localStorage.removeItem(HISTORY_KEY);
}

export function deleteHistoryItem(id: string) {
  try {
    const existing = getHistory();
    const updated = existing.filter((i) => i.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  } catch {
    // ignore
  }
}
