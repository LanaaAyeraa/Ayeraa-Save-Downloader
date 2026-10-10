import { useState, useEffect } from "react";
import {
  Download,
  ClipboardPaste,
  X,
  Loader2,
  Video,
  Music,
  Image as ImageIcon,
  Play,
  Share2,
} from "lucide-react";
import { Clipboard } from "@capacitor/clipboard";
import { Share } from "@capacitor/share";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { useToast } from "./ui/toast";
import { PlatformBar } from "./PlatformBar";
import {
  detectPlatform,
  scrapeMedia,
  type ScrapeResult,
  type DownloadItem,
} from "../services/scraperEngine";
import {
  downloadMediaItem,
  triggerHaptic,
} from "../services/downloadManager";

export function DownloaderView() {
  const { toast } = useToast();
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [scrapeResult, setScrapeResult] = useState<ScrapeResult | null>(null);

  // Download state
  const [activeDownload, setActiveDownload] = useState<{
    item: DownloadItem;
    percent: number;
    statusText: string;
  } | null>(null);

  const detectedPlatform = url ? detectPlatform(url) : undefined;

  // Auto-detect and handle Android Share Intent when launched
  useEffect(() => {
    const checkSharedUrl = async () => {
      try {
        const bridge = (window as any).MoriMainBridge || (window as any).AyeraaBridge;
        if (bridge?.getPendingHistoryList) {
          const list = JSON.parse(bridge.getPendingHistoryList() || "[]");
          if (list.length > 0 && list[0].url) {
            setUrl(list[0].url);
            bridge.clearPendingHistoryList();
            handleExtract(list[0].url);
          }
        }
      } catch {
        // ignore
      }
    };
    checkSharedUrl();
  }, []);

  const handlePaste = async () => {
    await triggerHaptic("medium");
    try {
      if ((window as any).Capacitor?.isNativePlatform?.()) {
        const text = await Clipboard.read();
        if (text?.value) {
          setUrl(text.value);
          toast({ title: "Pasted from clipboard", type: "info" });
          return;
        }
      }
      if (navigator.clipboard) {
        const text = await navigator.clipboard.readText();
        if (text) {
          setUrl(text);
          toast({ title: "Pasted from clipboard", type: "info" });
          return;
        }
      }
    } catch {
      toast({
        title: "Clipboard Access",
        description: "Please paste your URL directly into the box.",
        type: "error",
      });
    }
  };

  const handleClear = () => {
    setUrl("");
    setScrapeResult(null);
    triggerHaptic("medium");
  };

  const handleExtract = async (overrideUrl?: string) => {
    const targetUrl = overrideUrl || url;
    if (!targetUrl.trim()) {
      toast({ title: "Please enter a URL", type: "error" });
      return;
    }

    setIsLoading(true);
    setScrapeResult(null);
    await triggerHaptic("medium");

    try {
      const result = await scrapeMedia(targetUrl);
      if (result.status && result.downloads.length > 0) {
        setScrapeResult(result);
        await triggerHaptic("success");
        toast({
          title: "Media Extracted!",
          description: `Found ${result.downloads.length} download options.`,
          type: "success",
        });
      } else {
        toast({
          title: "Extraction Failed",
          description: result.message || "Could not find downloadable media.",
          type: "error",
        });
        await triggerHaptic("error");
      }
    } catch (err: any) {
      toast({
        title: "Error",
        description: err.message || "Failed to process URL.",
        type: "error",
      });
      await triggerHaptic("error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (item: DownloadItem) => {
    if (!scrapeResult) return;
    await triggerHaptic("medium");

    setActiveDownload({
      item,
      percent: 10,
      statusText: "Initializing download...",
    });

    const res = await downloadMediaItem(
      item,
      scrapeResult.title,
      scrapeResult.platform,
      (percent, statusText) => {
        setActiveDownload({ item, percent, statusText });
      }
    );

    if (res.success) {
      toast({
        title: "Download Complete!",
        description: `Saved as ${res.filename}`,
        type: "success",
      });
    } else {
      toast({
        title: "Download Failed",
        description: res.message || "Could not save file.",
        type: "error",
      });
    }

    setTimeout(() => {
      setActiveDownload(null);
    }, 2000);
  };

  const handleNativeShare = async (item: DownloadItem) => {
    if (!scrapeResult) return;
    try {
      await Share.share({
        title: scrapeResult.title,
        text: `Download ${scrapeResult.title} via Ayeraa Save Downloader`,
        url: item.url,
      });
    } catch {
      // fallback
    }
  };

  return (
    <div className="flex flex-col gap-5 pb-24">
      {/* Platform Chips */}
      <PlatformBar activePlatform={detectedPlatform} />

      {/* Main Input Card */}
      <Card className="border-border/70 bg-card/90 shadow-2xl backdrop-blur-xl">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base sm:text-lg">
              Paste Media Link
            </CardTitle>
            {detectedPlatform && detectedPlatform !== "unknown" && (
              <Badge variant="platform" className="capitalize text-xs">
                {detectedPlatform}
              </Badge>
            )}
          </div>
          <CardDescription>
            Supports TikTok, Instagram, YouTube, X, Spotify, and more.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="relative flex items-center">
            <Input
              type="url"
              placeholder="https://..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleExtract();
              }}
              className="pr-20 text-sm h-12 bg-background/80 border-border/80 focus-visible:ring-primary"
            />
            <div className="absolute right-1.5 flex items-center gap-1">
              {url ? (
                <button
                  type="button"
                  onClick={handleClear}
                  className="rounded-lg p-2 text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handlePaste}
                  className="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-primary bg-primary/10 hover:bg-primary/20 transition-colors"
                >
                  <ClipboardPaste className="h-3.5 w-3.5" />
                  <span>Paste</span>
                </button>
              )}
            </div>
          </div>

          <Button
            onClick={() => handleExtract()}
            disabled={isLoading || !url.trim()}
            variant="gradient"
            className="w-full h-12 text-base font-semibold shadow-purple-600/30"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                <span>Extracting Media...</span>
              </>
            ) : (
              <>
                <Download className="mr-2 h-5 w-5" />
                <span>Download Media</span>
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Active Download Progress Bar */}
      {activeDownload && (
        <Card className="border-primary/50 bg-primary/10 shadow-lg backdrop-blur-md animate-in slide-in-from-top-2">
          <CardContent className="p-4 space-y-2.5">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="flex items-center gap-1.5 text-primary-foreground">
                <Loader2 className="h-4 w-4 animate-spin text-pink-400" />
                <span>{activeDownload.statusText}</span>
              </span>
              <span className="text-white font-mono">{activeDownload.percent}%</span>
            </div>
            <Progress value={activeDownload.percent} className="h-2" />
          </CardContent>
        </Card>
      )}

      {/* Scrape Result Section */}
      {scrapeResult && (
        <Card className="border-border/80 bg-card/95 shadow-2xl backdrop-blur-xl animate-in slide-in-from-bottom-3">
          <CardContent className="p-4 sm:p-5 space-y-4">
            {/* Media Header (Thumbnail & Title) */}
            <div className="flex gap-3.5 items-start">
              {scrapeResult.thumbnail ? (
                <div className="relative h-20 w-20 sm:h-24 sm:w-24 shrink-0 overflow-hidden rounded-xl border border-border/80 bg-black shadow-md">
                  <img
                    src={scrapeResult.thumbnail}
                    alt={scrapeResult.title}
                    className="h-full w-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = "none";
                    }}
                  />
                  <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                    <Play className="h-6 w-6 text-white/80 fill-white/80 drop-shadow" />
                  </div>
                </div>
              ) : (
                <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-xl bg-secondary/80 border border-border">
                  <Video className="h-8 w-8 text-muted-foreground" />
                </div>
              )}

              <div className="flex flex-col justify-between overflow-hidden flex-1 min-w-0">
                <div>
                  <Badge variant="platform" className="capitalize text-[10px] mb-1">
                    {scrapeResult.platform}
                  </Badge>
                  <h3 className="text-sm sm:text-base font-semibold leading-snug line-clamp-2 text-white">
                    {scrapeResult.title}
                  </h3>
                  {scrapeResult.author && (
                    <p className="text-xs text-muted-foreground mt-0.5 truncate">
                      by {scrapeResult.author}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Download Options List */}
            <div className="space-y-2 pt-2 border-t border-border/50">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                Available Formats & Qualities
              </span>

              <div className="grid grid-cols-1 gap-2">
                {scrapeResult.downloads.map((item, idx) => {
                  const typeUpper = item.type.toUpperCase();
                  const isAudio =
                    typeUpper.includes("MP3") || typeUpper.includes("AUDIO");
                  const isPhoto =
                    typeUpper.includes("PHOTO") || typeUpper.includes("IMAGE");
                  const isHD =
                    typeUpper.includes("1080") || typeUpper.includes("HD");

                  return (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-xl border border-border/60 bg-secondary/30 p-2.5 sm:p-3 hover:bg-secondary/60 transition-all duration-200"
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div
                          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
                            isAudio
                              ? "bg-emerald-500/20 text-emerald-400"
                              : isPhoto
                              ? "bg-amber-500/20 text-amber-400"
                              : "bg-purple-500/20 text-purple-400"
                          }`}
                        >
                          {isAudio ? (
                            <Music className="h-4 w-4" />
                          ) : isPhoto ? (
                            <ImageIcon className="h-4 w-4" />
                          ) : (
                            <Video className="h-4 w-4" />
                          )}
                        </div>
                        <div className="truncate">
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs sm:text-sm font-semibold text-white">
                              {item.type}
                            </span>
                            {isHD && (
                              <Badge
                                variant="outline"
                                className="text-[9px] py-0 px-1 border-purple-500/40 text-purple-300 font-bold"
                              >
                                HD
                              </Badge>
                            )}
                          </div>
                          {item.size && (
                            <span className="text-[11px] text-muted-foreground">
                              {item.size}
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-1.5 shrink-0">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleNativeShare(item)}
                          className="h-8 w-8 p-0 rounded-lg text-muted-foreground hover:text-white"
                        >
                          <Share2 className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleDownload(item)}
                          disabled={activeDownload !== null}
                          className="h-8 rounded-lg px-3 text-xs font-semibold bg-primary hover:bg-primary/90 text-white"
                        >
                          <Download className="mr-1.5 h-3.5 w-3.5" />
                          <span>Save</span>
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
