import { describe, it, expect } from "vitest";
import {
  compareVersions,
  findApkAsset,
  parseReleaseUpdate,
} from "./updaterService";

describe("updaterService - compareVersions", () => {
  it("correctly identifies newer version with 'v' prefix", () => {
    expect(compareVersions("v1.2.0", "1.1.0")).toBeGreaterThan(0);
    expect(compareVersions("1.3.0", "v1.2.0")).toBeGreaterThan(0);
    expect(compareVersions("v2.0.0", "1.2.0")).toBeGreaterThan(0);
  });

  it("upgrades legacy 4.x installs to v1.2.0", () => {
    expect(compareVersions("v1.2.0", "4.4.0")).toBeGreaterThan(0);
    expect(compareVersions("1.2.0", "4.4.0")).toBeGreaterThan(0);
  });

  it("correctly identifies equal versions", () => {
    expect(compareVersions("v1.2.0", "1.2.0")).toBe(0);
    expect(compareVersions("1.2", "1.2.0")).toBe(0);
    expect(compareVersions("v1.0.0", "v1.0.0")).toBe(0);
  });

  it("correctly identifies older versions", () => {
    expect(compareVersions("1.1.0", "1.2.0")).toBeLessThan(0);
    expect(compareVersions("v1.0.0", "1.1.0")).toBeLessThan(0);
  });

  it("handles patch version increments", () => {
    expect(compareVersions("v1.2.1", "1.2.0")).toBeGreaterThan(0);
    expect(compareVersions("1.2.10", "1.2.2")).toBeGreaterThan(0);
  });
});

describe("updaterService - findApkAsset", () => {
  it("picks the best matching APK asset from release assets", () => {
    const assets = [
      { name: "Ayeraa-Save-Downloader-Windows.zip", browser_download_url: "https://example.com/win.zip", size: 5000 },
      { name: "Ayeraa-Save-Downloader-Pro.apk", browser_download_url: "https://example.com/pro.apk", size: 12000 },
      { name: "Ayeraa-Save-Downloader.apk", browser_download_url: "https://example.com/app.apk", size: 10000 },
    ];
    const asset = findApkAsset(assets);
    expect(asset).not.toBeNull();
    expect(asset?.downloadUrl).toBe("https://example.com/pro.apk");
  });

  it("falls back to any .apk file if specific naming is absent", () => {
    const assets = [
      { name: "source.tar.gz", browser_download_url: "https://example.com/src.tar.gz", size: 1000 },
      { name: "mori-release.apk", browser_download_url: "https://example.com/mori.apk", size: 8000 },
    ];
    const asset = findApkAsset(assets);
    expect(asset).not.toBeNull();
    expect(asset?.downloadUrl).toBe("https://example.com/mori.apk");
  });

  it("returns null if no APK asset is found", () => {
    const assets = [
      { name: "Windows.exe", browser_download_url: "https://example.com/win.exe", size: 2000 },
    ];
    const asset = findApkAsset(assets);
    expect(asset).toBeNull();
  });
});

describe("updaterService - parseReleaseUpdate", () => {
  const mockRelease = {
    tag_name: "v1.2.0",
    name: "Ayeraa Save Downloader v1.2.0",
    body: "### What's new\n- Fast auto updates\n- Bug fixes",
    published_at: "2026-10-11T00:00:00Z",
    assets: [
      {
        name: "Ayeraa-Save-Downloader.apk",
        browser_download_url: "https://github.com/downloads/ayeraa.apk",
        size: 35000000,
      },
    ],
  };

  it("detects available update when remote tag is higher", () => {
    const update = parseReleaseUpdate(mockRelease, "1.1.0");
    expect(update).not.toBeNull();
    expect(update?.hasUpdate).toBe(true);
    expect(update?.latestVersion).toBe("v1.2.0");
    expect(update?.apkUrl).toBe("https://github.com/downloads/ayeraa.apk");
    expect(update?.apkSize).toBe(35000000);
  });

  it("marks hasUpdate as false when already on the latest version", () => {
    const update = parseReleaseUpdate(mockRelease, "1.2.0");
    expect(update).not.toBeNull();
    expect(update?.hasUpdate).toBe(false);
  });
});
