// Ayera Downloader Pro - Chrome Integration Module (Background Service Worker)
const BRIDGE_URL = "http://127.0.0.1:18791";

const DEFAULT_EXTENSIONS = [
  "zip", "rar", "7z", "tar", "gz", "bz2", "xz",
  "iso", "bin", "img", "vhd",
  "exe", "msi", "apk", "deb", "rpm", "dmg", "pkg",
  "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
  "mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "ts", "m4v",
  "mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"
];

// Initialize configuration
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(["auto_intercept", "intercept_extensions", "floating_bar"], (res) => {
    if (res.auto_intercept === undefined) {
      chrome.storage.local.set({ auto_intercept: true });
    }
    if (!res.intercept_extensions) {
      chrome.storage.local.set({ intercept_extensions: DEFAULT_EXTENSIONS });
    }
    if (res.floating_bar === undefined) {
      chrome.storage.local.set({ floating_bar: true });
    }
  });

  // Setup IDM-style context menus
  setupContextMenus();
});

function setupContextMenus() {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "ayera-download-link",
      title: "Download with Ayera Downloader Pro (32 Lanes)",
      contexts: ["link"]
    });

    chrome.contextMenus.create({
      id: "ayera-download-media",
      title: "Download Video/Audio with Ayera Pro",
      contexts: ["video", "audio"]
    });

    chrome.contextMenus.create({
      id: "ayera-download-image",
      title: "Download Image with Ayera Pro",
      contexts: ["image"]
    });
  });
}

// Handle Context Menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  let targetUrl = null;
  if (info.menuItemId === "ayera-download-link" && info.linkUrl) {
    targetUrl = info.linkUrl;
  } else if (info.menuItemId === "ayera-download-media" && info.srcUrl) {
    targetUrl = info.srcUrl;
  } else if (info.menuItemId === "ayera-download-image" && info.srcUrl) {
    targetUrl = info.srcUrl;
  }

  if (targetUrl) {
    sendDownloadToAyera(targetUrl, null, tab ? tab.url : null);
  }
});

// Check if Ayera Desktop app is online
async function checkAyeraOnline() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1200);
    const resp = await fetch(`${BRIDGE_URL}/status`, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (resp.ok) {
      const data = await resp.json();
      return data.status === "ok";
    }
  } catch (e) {
    // Offline or unreachable
  }
  return false;
}

// Send download payload to Ayera Desktop via Local Bridge
async function sendDownloadToAyera(url, filename = null, referrer = null) {
  try {
    const payload = {
      url: url,
      filename: filename || extractFilenameFromUrl(url),
      referrer: referrer || "",
      start_now: true
    };

    const resp = await fetch(`${BRIDGE_URL}/add-download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (resp.ok) {
      const result = await resp.json();
      console.log("[Ayera Extension] Download queued to Ayera Pro:", result);
      showNotification("Ayera Downloader Pro", "Download dialihkan ke 32-Lane Accelerator!");
      return true;
    }
  } catch (err) {
    console.warn("[Ayera Extension] Failed to reach Ayera Desktop:", err);
  }
  return false;
}

function extractFilenameFromUrl(url) {
  try {
    const cleanUrl = url.split("?")[0].split("#")[0];
    const parts = cleanUrl.split("/");
    const last = parts[parts.length - 1];
    if (last && last.length > 0) {
      return decodeURIComponent(last);
    }
  } catch (e) {}
  return "download.bin";
}

function showNotification(title, message) {
  // Badge notification on action icon
  chrome.action.setBadgeText({ text: "32⚡" });
  chrome.action.setBadgeBackgroundColor({ color: "#10B981" });
  setTimeout(() => {
    chrome.action.setBadgeText({ text: "" });
  }, 4000);
}

// Intercept browser native downloads (IDM Catching mechanism)
const recentlyCaughtUrls = new Set();

chrome.downloads.onCreated.addListener(async (downloadItem) => {
  const url = downloadItem.finalUrl || downloadItem.url;
  if (!url || url.startsWith("blob:") || url.startsWith("data:") || recentlyCaughtUrls.has(url)) {
    return;
  }

  // Check user settings
  const config = await chrome.storage.local.get(["auto_intercept", "intercept_extensions"]);
  if (!config.auto_intercept) {
    return;
  }

  const exts = config.intercept_extensions || DEFAULT_EXTENSIONS;
  const filename = downloadItem.filename || extractFilenameFromUrl(url);
  const fileExt = filename.split(".").pop().toLowerCase();

  // If file extension is in intercept list
  if (exts.includes(fileExt)) {
    const isOnline = await checkAyeraOnline();
    if (isOnline) {
      recentlyCaughtUrls.add(url);
      setTimeout(() => recentlyCaughtUrls.delete(url), 5000);

      // Cancel Chrome's slow native download
      try {
        chrome.downloads.cancel(downloadItem.id, () => {
          chrome.downloads.erase({ id: downloadItem.id });
        });
      } catch (e) {}

      // Forward to Ayera Downloader 32-channel accelerator
      await sendDownloadToAyera(url, filename, downloadItem.referrer);
    }
  }
});

// Communication with Content Script and Popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "CHECK_STATUS") {
    checkAyeraOnline().then((online) => sendResponse({ online }));
    return true;
  }

  if (request.type === "TRIGGER_DOWNLOAD") {
    sendDownloadToAyera(request.url, request.filename, sender.tab ? sender.tab.url : null)
      .then((success) => sendResponse({ success }));
    return true;
  }

  if (request.type === "GET_CONFIG") {
    chrome.storage.local.get(null, (items) => sendResponse(items));
    return true;
  }
});
