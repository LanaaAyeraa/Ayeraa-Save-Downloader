import { useState } from "react";
import {
  Sliders,
  Vibrate,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { useToast } from "./ui/toast";
import { triggerHaptic } from "../services/downloadManager";

export function SettingsView() {
  const { toast } = useToast();

  const [tiktokSource, setTiktokSource] = useState(
    localStorage.getItem("ayeraa_tiktok_source") || "tikdownloader"
  );
  const [youtubeSource, setYoutubeSource] = useState(
    localStorage.getItem("ayeraa_youtube_source") || "gg"
  );
  const [instagramSource, setInstagramSource] = useState(
    localStorage.getItem("ayeraa_instagram_source") || "snapsave"
  );
  const [hapticEnabled, setHapticEnabled] = useState(
    localStorage.getItem("mori_haptic") !== "false"
  );

  const handleSourceChange = (key: string, val: string, setter: (v: string) => void) => {
    setter(val);
    localStorage.setItem(key, val);
    triggerHaptic("medium");
    toast({ title: "Settings saved", type: "success" });
  };

  const toggleHaptic = () => {
    const nextVal = !hapticEnabled;
    setHapticEnabled(nextVal);
    localStorage.setItem("mori_haptic", nextVal ? "true" : "false");
    triggerHaptic("medium");
  };

  return (
    <div className="flex flex-col gap-5 pb-24">
      {/* Engine & Source Selection */}
      <Card className="border-border/70 bg-card/90">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Sliders className="h-4 w-4 text-purple-400" />
            <span>Extractor Servers</span>
          </CardTitle>
          <CardDescription>
            Choose fallback servers in case one gets rate-limited.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* TikTok Source */}
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium text-white">TikTok Source</span>
              <p className="text-xs text-muted-foreground">Default extractor server</p>
            </div>
            <select
              value={tiktokSource}
              onChange={(e) =>
                handleSourceChange("ayeraa_tiktok_source", e.target.value, setTiktokSource)
              }
              className="bg-secondary text-foreground text-xs font-semibold rounded-lg px-2.5 py-1.5 border border-border"
            >
              <option value="tikdownloader">TikDownloader (Fast HD)</option>
              <option value="tiktokio">TikTokIO (Mirror)</option>
            </select>
          </div>

          {/* YouTube Source */}
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium text-white">YouTube Source</span>
              <p className="text-xs text-muted-foreground">Audio & Video resolution engine</p>
            </div>
            <select
              value={youtubeSource}
              onChange={(e) =>
                handleSourceChange("ayeraa_youtube_source", e.target.value, setYoutubeSource)
              }
              className="bg-secondary text-foreground text-xs font-semibold rounded-lg px-2.5 py-1.5 border border-border"
            >
              <option value="gg">ytmp3.gg (High Speed)</option>
              <option value="mobi">ytmp3.mobi (Fallback)</option>
            </select>
          </div>

          {/* Instagram Source */}
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium text-white">Instagram Source</span>
              <p className="text-xs text-muted-foreground">Reels & Post carousel</p>
            </div>
            <select
              value={instagramSource}
              onChange={(e) =>
                handleSourceChange("ayeraa_instagram_source", e.target.value, setInstagramSource)
              }
              className="bg-secondary text-foreground text-xs font-semibold rounded-lg px-2.5 py-1.5 border border-border"
            >
              <option value="snapsave">SnapSave (Standard)</option>
              <option value="indown">InDown (Mirror)</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Preferences */}
      <Card className="border-border/70 bg-card/90">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Vibrate className="h-4 w-4 text-emerald-400" />
            <span>Preferences</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium text-white">Haptic Feedback</span>
              <p className="text-xs text-muted-foreground">Vibrate on button clicks and completed downloads</p>
            </div>
            <button
              onClick={toggleHaptic}
              className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors duration-200 ${
                hapticEnabled ? "bg-primary" : "bg-secondary"
              }`}
            >
              <div
                className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-200 ${
                  hapticEnabled ? "translate-x-6" : "translate-x-0"
                }`}
              />
            </button>
          </div>
        </CardContent>
      </Card>

      {/* App Info */}
      <Card className="border-border/70 bg-card/90">
        <CardContent className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">App Name</span>
            <span className="text-xs font-semibold text-white">Ayeraa Save Downloader</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Version</span>
            <Badge variant="outline" className="text-[10px] font-bold">
              v4.4.0 (shadcn/ui edition)
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Engine Architecture</span>
            <span className="text-xs font-semibold text-purple-400">Capacitor 7 + Native Bridge</span>
          </div>
          <div className="pt-2 border-t border-border/40 text-center">
            <p className="text-[11px] text-muted-foreground">
              Universal Media Engine. Powered by React &amp; shadcn/ui.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
