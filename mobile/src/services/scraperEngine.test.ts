import { describe, it, expect } from "vitest";
import {
  cleanUrl,
  extractCleanUrl,
  detectPlatform,
  serializeData,
} from "./scraperEngine";

describe("Scraper Engine Utilities", () => {
  it("detects platforms accurately", () => {
    expect(detectPlatform("https://www.tiktok.com/@user/video/123456789")).toBe(
      "tiktok"
    );
    expect(detectPlatform("https://instagram.com/reel/C-xyz123/?igsh=abc")).toBe(
      "instagram"
    );
    expect(detectPlatform("https://youtu.be/dQw4w9WgXcQ")).toBe("youtube");
    expect(detectPlatform("https://www.youtube.com/watch?v=dQw4w9WgXcQ")).toBe(
      "youtube"
    );
    expect(detectPlatform("https://x.com/user/status/123456789")).toBe(
      "twitter"
    );
    expect(
      detectPlatform("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")
    ).toBe("spotify");
    expect(detectPlatform("https://www.facebook.com/watch/?v=123456")).toBe(
      "facebook"
    );
    expect(detectPlatform("https://pin.it/7xYZabc")).toBe("pinterest");
    expect(detectPlatform("https://threads.net/@user/post/123456")).toBe(
      "threads"
    );
    expect(detectPlatform("https://www.bilibili.com/video/BV123456")).toBe(
      "bilibili"
    );
    expect(detectPlatform("https://www.reddit.com/r/funny/comments/123/test/")).toBe(
      "reddit"
    );
    expect(detectPlatform("https://terabox.com/s/1abc-xyz")).toBe("terabox");
  });

  it("extracts and cleans URLs from user text", () => {
    const rawText = "Check out this TikTok video! https://vt.tiktok.com/ZS2xyz/ and tell me";
    expect(extractCleanUrl(rawText)).toBe("https://vt.tiktok.com/ZS2xyz");
  });

  it("strips tracker parameters while preserving core query params", () => {
    const igUrl = "https://www.instagram.com/p/C-xyz123/?igsh=12345&utm_source=ig_web_copy_link";
    expect(cleanUrl(igUrl)).toBe("https://www.instagram.com/p/C-xyz123");

    const ytUrl = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtu.be&si=abc123";
    expect(cleanUrl(ytUrl)).toBe("https://www.youtube.com/watch?v=dQw4w9WgXcQ");
  });

  it("serializes form parameters correctly", () => {
    const serialized = serializeData({ q: "test media", lang: "id" });
    expect(serialized).toBe("q=test%20media&lang=id");
  });
});
