export const CURRENT_APP_VERSION = "1.2.0";
export const GITHUB_REPO = "LanaaAyeraa/Ayeraa-Save-Downloader";

export interface ReleaseAsset {
  name: string;
  browser_download_url: string;
  size: number;
}

export interface UpdateInfo {
  hasUpdate: boolean;
  currentVersion: string;
  latestVersion: string;
  title: string;
  body: string;
  apkUrl: string;
  apkSize: number;
  publishedAt: string;
}

declare global {
  interface Window {
    MoriMainBridge?: {
      downloadAndInstallApk?: (url: string, callbackId: string) => void;
      installApk?: (path: string) => boolean;
      canInstallPackages?: () => boolean;
      requestInstallPackagesPermission?: () => void;
    };
    __ayeraaUpdateProgress?: (percent: number, loaded: number, total: number) => void;
    __ayeraaUpdateCallback?: Record<string, (result: { success: boolean; error?: string }) => void>;
  }
}

/**
 * Compare two semver strings (e.g. "v1.2.0" and "1.1.0").
 * Returns:
 *   1 if a > b
 *  -1 if a < b
 *   0 if a == b
 */
export function compareVersions(a: string, b: string): number {
  let cleanA = a.replace(/^[vV]/, "").trim();
  let cleanB = b.replace(/^[vV]/, "").trim();

  // Normalize legacy Mori version strings (4.x) to 1.1.0 so they upgrade seamlessly
  if (cleanA.startsWith("4.")) cleanA = "1.1.0";
  if (cleanB.startsWith("4.")) cleanB = "1.1.0";

  // Split on dots or hyphens
  const partsA = cleanA.split(/[.-]/).map((p) => {
    const num = parseInt(p, 10);
    return isNaN(num) ? 0 : num;
  });
  const partsB = cleanB.split(/[.-]/).map((p) => {
    const num = parseInt(p, 10);
    return isNaN(num) ? 0 : num;
  });

  const maxLen = Math.max(partsA.length, partsB.length);
  for (let i = 0; i < maxLen; i++) {
    const numA = partsA[i] || 0;
    const numB = partsB[i] || 0;
    if (numA > numB) return 1;
    if (numA < numB) return -1;
  }
  return 0;
}

/**
 * Find the most suitable APK asset from GitHub Release assets list.
 */
export function findApkAsset(
  assets: ReleaseAsset[]
): { name: string; downloadUrl: string; size: number } | null {
  if (!assets || !Array.isArray(assets) || assets.length === 0) return null;

  const apkAssets = assets.filter(
    (a) => a.name && a.name.toLowerCase().endsWith(".apk")
  );

  if (apkAssets.length === 0) return null;

  // Priority order:
  // 1. Ayeraa-Save-Downloader-Pro.apk
  // 2. Ayeraa-Save-Downloader*.apk
  // 3. Any APK
  const proApk = apkAssets.find((a) =>
    a.name.toLowerCase().includes("pro")
  );
  if (proApk) {
    return {
      name: proApk.name,
      downloadUrl: proApk.browser_download_url,
      size: proApk.size,
    };
  }

  const ayeraaApk = apkAssets.find((a) =>
    a.name.toLowerCase().includes("ayeraa")
  );
  if (ayeraaApk) {
    return {
      name: ayeraaApk.name,
      downloadUrl: ayeraaApk.browser_download_url,
      size: ayeraaApk.size,
    };
  }

  const fallback = apkAssets[0];
  return {
    name: fallback.name,
    downloadUrl: fallback.browser_download_url,
    size: fallback.size,
  };
}

/**
 * Parse GitHub release payload into structured UpdateInfo
 */
export function parseReleaseUpdate(
  releaseData: any,
  currentVersion: string = CURRENT_APP_VERSION
): UpdateInfo | null {
  if (!releaseData) return null;

  const tag = releaseData.tag_name || releaseData.name || "";
  const apkAsset = findApkAsset(releaseData.assets || []);
  if (!apkAsset) return null;

  const hasUpdate = compareVersions(tag, currentVersion) > 0;

  return {
    hasUpdate,
    currentVersion,
    latestVersion: tag,
    title: releaseData.name || tag,
    body: releaseData.body || "Pembaruan versi terbaru untuk Ayeraa Save Downloader.",
    apkUrl: apkAsset.downloadUrl,
    apkSize: apkAsset.size,
    publishedAt: releaseData.published_at || new Date().toISOString(),
  };
}

/**
 * Check GitHub repository for the latest release
 */
export async function checkForUpdate(
  currentVersion: string = CURRENT_APP_VERSION
): Promise<UpdateInfo | null> {
  try {
    const url = `https://api.github.com/repos/${GITHUB_REPO}/releases/latest`;
    const res = await fetch(url, {
      headers: {
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!res.ok) {
      console.warn("GitHub release check failed:", res.status);
      return null;
    }

    const data = await res.json();
    return parseReleaseUpdate(data, currentVersion);
  } catch (err) {
    console.error("checkForUpdate error:", err);
    return null;
  }
}

/**
 * Trigger APK installation via native Android Bridge (or browser download)
 */
export function triggerApkInstallation(
  apkUrl: string,
  onProgress?: (percent: number, loaded: number, total: number) => void
): Promise<{ success: boolean; error?: string }> {
  return new Promise((resolve) => {
    if (window.MoriMainBridge && typeof window.MoriMainBridge.downloadAndInstallApk === "function") {
      const callbackId = "update_" + Date.now();

      if (!window.__ayeraaUpdateCallback) {
        window.__ayeraaUpdateCallback = {};
      }

      window.__ayeraaUpdateProgress = (percent, loaded, total) => {
        if (onProgress) {
          onProgress(percent, loaded, total);
        }
      };

      window.__ayeraaUpdateCallback[callbackId] = (result) => {
        delete window.__ayeraaUpdateCallback?.[callbackId];
        resolve(result);
      };

      try {
        window.MoriMainBridge.downloadAndInstallApk(apkUrl, callbackId);
      } catch (e: any) {
        resolve({ success: false, error: e.message || String(e) });
      }
    } else {
      // Fallback for web or desktop preview: open direct download link
      window.open(apkUrl, "_blank");
      resolve({ success: true });
    }
  });
}

export function isVersionIgnored(version: string): boolean {
  try {
    return localStorage.getItem("ayeraa_ignored_update_version") === version;
  } catch {
    return false;
  }
}

export function ignoreVersion(version: string): void {
  try {
    localStorage.setItem("ayeraa_ignored_update_version", version);
  } catch {}
}
