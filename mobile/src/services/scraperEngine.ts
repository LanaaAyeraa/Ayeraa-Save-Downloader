// Unified Scraper Engine for Ayeraa Save Downloader
// Compatible with Mori core scrapers and direct API clients

export type PlatformType =
  | "tiktok"
  | "instagram"
  | "youtube"
  | "twitter"
  | "spotify"
  | "facebook"
  | "pinterest"
  | "threads"
  | "bilibili"
  | "douyin"
  | "rednote"
  | "reddit"
  | "terabox"
  | "unknown";

export interface DownloadItem {
  type: string;
  url: string;
  quality?: string;
  thumbnail?: string;
  size?: string;
  filename?: string;
  isMirror?: boolean;
}

export interface ScrapeResult {
  status: boolean;
  title: string;
  author?: string;
  thumbnail?: string;
  sourceUrl: string;
  platform: PlatformType;
  downloads: DownloadItem[];
  message?: string;
}

// User Agent constants
export const CHROME_DESKTOP_UA =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36";
export const CHROME_MOBILE_UA =
  "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1";
export const CHROME_UA =
  "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36";

export function getUserAgent(): string {
  const mode = localStorage.getItem("mori_user_agent") || "default";
  if (mode === "desktop") return CHROME_DESKTOP_UA;
  if (mode === "safari") return CHROME_MOBILE_UA;
  return CHROME_UA;
}

export function cleanUrl(url: string): string {
  if (!url) return "";
  try {
    const u = new URL(url);
    const trackerParams = [
      "igsh",
      "utm_source",
      "utm_medium",
      "utm_campaign",
      "utm_term",
      "utm_content",
      "s",
      "t",
      "si",
      "feature",
    ];
    trackerParams.forEach((p) => u.searchParams.delete(p));
    if (u.hostname.includes("tiktok.com")) {
      u.search = "";
    } else if (u.hostname.includes("youtube.com") && u.searchParams.has("v")) {
      const v = u.searchParams.get("v");
      u.search = "";
      if (v) u.searchParams.set("v", v);
    }
    return u.href.replace(/\/$/, "");
  } catch {
    return url.split("?")[0].replace(/\/$/, "");
  }
}

export function extractCleanUrl(text: string): string {
  if (!text || typeof text !== "string") return "";
  const match = text.match(/https?:\/\/[^\s]+/);
  let clean = match ? match[0] : text.trim();
  if (!clean) return "";
  if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
    clean = "https://" + clean;
  }
  return cleanUrl(clean);
}

export function detectPlatform(rawUrl: string): PlatformType {
  let hostname = "";
  try {
    hostname = new URL(rawUrl.startsWith("http") ? rawUrl : `https://${rawUrl}`).hostname.toLowerCase();
  } catch {
    hostname = rawUrl.toLowerCase();
  }

  if (hostname.includes("tiktok.com") || rawUrl.includes("douyin.com/v/")) return "tiktok";
  if (hostname.includes("douyin.com")) return "douyin";
  if (hostname.includes("instagram.com")) return "instagram";
  if (hostname.includes("youtube.com") || hostname.includes("youtu.be")) return "youtube";
  if (
    hostname === "twitter.com" ||
    hostname.endsWith(".twitter.com") ||
    hostname === "x.com" ||
    hostname.endsWith(".x.com") ||
    hostname === "t.co" ||
    hostname.endsWith(".t.co")
  ) {
    return "twitter";
  }
  if (hostname.includes("spotify.com") || hostname.includes("spotify.link")) return "spotify";
  if (hostname.includes("facebook.com") || hostname.includes("fb.watch") || hostname.includes("fb.com")) return "facebook";
  if (hostname.includes("pinterest.com") || hostname.includes("pin.it")) return "pinterest";
  if (hostname.includes("threads.net") || hostname.includes("threads.com")) return "threads";
  if (hostname.includes("bilibili.com") || hostname.includes("b23.tv")) return "bilibili";
  if (hostname.includes("xiaohongshu.com") || hostname.includes("rednote.com") || hostname.includes("xhslink.com")) return "rednote";
  if (hostname.includes("reddit.com") || hostname.includes("redd.it")) return "reddit";
  if (hostname.includes("terabox") || hostname.includes("1024tera") || hostname.includes("nephobox")) return "terabox";
  return "unknown";
}

export function serializeData(obj: Record<string, any>): string {
  return Object.keys(obj)
    .map((k) => encodeURIComponent(k) + "=" + encodeURIComponent(obj[k]))
    .join("&");
}

export function getCookiesFromHeaders(headers: Record<string, string>): string {
  const raw = headers["Set-Cookie"] || headers["set-cookie"] || "";
  if (!raw) return "";
  if (Array.isArray(raw)) return raw.map((c) => c.split(";")[0]).join("; ");
  return raw
    .split(/,(?=\s*[^;,=]+=[^;]*)/)
    .map((c) => c.trim().split(";")[0])
    .filter((c) => c && c.includes("="))
    .join("; ");
}

let coreScrapersPromise: Promise<any> | null = null;

async function loadScraperCore(): Promise<any> {
  if (coreScrapersPromise) return coreScrapersPromise;

  coreScrapersPromise = (async () => {
    // 1. Setup window.__moriDeps
    const capacitorHttp = (window as any).Capacitor?.Plugins?.CapacitorHttp;
    (window as any).__moriDeps = {
      utils: {
        getUserAgent,
        CHROME_UA,
        CHROME_DESKTOP_UA,
        serializeData,
        cleanUrl,
        extractCleanUrl,
        getCleanUrl: extractCleanUrl,
        getCookiesFromHeaders,
        CapacitorHttp: capacitorHttp,
      },
      urlUtils: {
        cleanUrl,
        extractCleanUrl,
        getCleanUrl: extractCleanUrl,
      },
      core: {
        currentLang: "en",
      },
    };

    // 2. Fetch bundle.js text
    const candidates = [
      "/js/scrapers/bundle.js",
      "js/scrapers/bundle.js",
      "./js/scrapers/bundle.js",
      "file:///android_asset/public/js/scrapers/bundle.js",
    ];

    let bundleText = "";
    for (const u of candidates) {
      try {
        const res = await fetch(u);
        if (res.ok) {
          bundleText = await res.text();
          break;
        }
      } catch {
        // continue
      }
    }

    if (!bundleText) {
      throw new Error("Could not load scraper bundle script.");
    }

    // 3. Execute and evaluate bundle
    const fn = new Function(
      bundleText +
        "\nreturn typeof __MoriCoreScrapers !== 'undefined' ? __MoriCoreScrapers : (typeof window !== 'undefined' ? window.__MoriCoreScrapers : null);"
    );
    const mod = fn();
    if (!mod) throw new Error("Failed to initialize core scrapers.");
    return mod;
  })();

  return coreScrapersPromise;
}

export async function scrapeMedia(rawInputUrl: string): Promise<ScrapeResult> {
  const url = extractCleanUrl(rawInputUrl);
  if (!url) {
    return {
      status: false,
      title: "Invalid URL",
      sourceUrl: rawInputUrl,
      platform: "unknown",
      downloads: [],
      message: "Please enter a valid media link.",
    };
  }

  const platform = detectPlatform(url);
  const core = await loadScraperCore();

  try {
    let rawResult: any = null;

    switch (platform) {
      case "tiktok": {
        // Try tikdownloader first, then fallback to tiktokio
        try {
          core.setTikTokSource("tikdownloader");
          rawResult = await core.scrapeTikTok(url);
        } catch {
          // fallback
        }
        if (!rawResult || !rawResult.status) {
          core.setTikTokSource("tiktokio");
          rawResult = await core.scrapeTikTok(url);
        }
        break;
      }

      case "instagram": {
        // Try snapsave, then fallback to indown
        try {
          core.setInstagramSource("snapsave");
          rawResult = await core.scrapeInstagram(url);
        } catch {
          // fallback
        }
        if (!rawResult || !rawResult.status) {
          core.setInstagramSource("indown");
          rawResult = await core.scrapeInstagram(url);
        }
        break;
      }

      case "youtube": {
        // Try gg first, then fallback to mobi
        try {
          core.setYouTubeSource("gg");
          rawResult = await core.scrapeYouTube(url);
        } catch {
          // fallback
        }
        if (!rawResult || !rawResult.status) {
          core.setYouTubeSource("mobi");
          rawResult = await core.scrapeYouTube(url);
        }
        break;
      }

      case "twitter": {
        // Try savetwt, then fallback to tvd
        try {
          core.setTwitterSource("savetwt");
          rawResult = await core.scrapeTwitter(url);
        } catch {
          // fallback
        }
        if (!rawResult || !rawResult.status) {
          core.setTwitterSource("tvd");
          rawResult = await core.scrapeTwitter(url);
        }
        break;
      }

      case "spotify": {
        // Try soundloaders first, then fallback to spotidown
        try {
          core.setSpotifySource("soundloaders");
          rawResult = await core.scrapeSpotify(url);
        } catch {
          // fallback
        }
        if (!rawResult || !rawResult.status) {
          core.setSpotifySource("spotidown");
          rawResult = await core.scrapeSpotify(url);
        }
        break;
      }

      case "facebook":
        rawResult = await core.scrapeFacebook(url);
        break;

      case "pinterest":
        rawResult = await core.scrapePinterest(url);
        break;

      case "threads":
        rawResult = await core.scrapeThreads(url);
        break;

      case "bilibili":
        rawResult = await core.scrapeBilibili(url);
        break;

      case "douyin":
        rawResult = await core.scrapeDouyin(url);
        break;

      case "rednote":
        rawResult = await core.scrapeRedNote(url);
        break;

      case "reddit":
        rawResult = await core.scrapeReddit(url);
        break;

      case "terabox":
        rawResult = await core.scrapeTeraBox(url);
        break;

      default:
        // Try generic video scrape or snap
        throw new Error(
          "Platform not recognized. Please check the URL (TikTok, Instagram, YouTube, X, Spotify, etc.)."
        );
    }

    if (!rawResult || !rawResult.status) {
      return {
        status: false,
        title: "Extraction Failed",
        sourceUrl: url,
        platform,
        downloads: [],
        message: rawResult?.message || "Failed to extract media links.",
      };
    }

    const resData = rawResult.result || rawResult.data || rawResult;
    const rawDownloads = resData.downloads || [];

    const downloads: DownloadItem[] = rawDownloads.map((item: any) => ({
      type: item.type || item.quality || "Media",
      url: item.url || "",
      quality: item.quality,
      thumbnail: item.thumbnail || resData.thumbnail,
      size: item.size || item.sizeFormatted,
      filename: item.filename,
      isMirror: Boolean(item.isMirror),
    }));

    return {
      status: true,
      title: resData.title || "Ayeraa Media",
      author: resData.author || resData.uploader,
      thumbnail: resData.thumbnail || (downloads[0]?.thumbnail ?? ""),
      sourceUrl: url,
      platform,
      downloads,
    };
  } catch (err: any) {
    return {
      status: false,
      title: "Error",
      sourceUrl: url,
      platform,
      downloads: [],
      message: err.message || "An unexpected error occurred during extraction.",
    };
  }
}
