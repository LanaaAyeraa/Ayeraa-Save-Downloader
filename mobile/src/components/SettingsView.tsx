import { useState } from "react";
import {
  Sliders,
  Vibrate,
  RefreshCw,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { useToast } from "./ui/toast";
import { triggerHaptic } from "../services/downloadManager";
import {
  checkForUpdate,
  type UpdateInfo,
  CURRENT_APP_VERSION,
} from "../services/updaterService";

interface SettingsViewProps {
  onUpdateAvailable?: (info: UpdateInfo) => void;
}

export function SettingsView({ onUpdateAvailable }: SettingsViewProps) {
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
  const [autoCheckUpdate, setAutoCheckUpdate] = useState(
    localStorage.getItem("ayeraa_auto_check_update") !== "false"
  );
  const [checkingUpdate, setCheckingUpdate] = useState(false);

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

  const toggleAutoCheckUpdate = () => {
    const nextVal = !autoCheckUpdate;
    setAutoCheckUpdate(nextVal);
    localStorage.setItem("ayeraa_auto_check_update", nextVal ? "true" : "false");
    triggerHaptic("medium");
    toast({
      title: nextVal ? "Pemeriksaan otomatis diaktifkan" : "Pemeriksaan otomatis dinonaktifkan",
      type: "info",
    });
  };

  const handleManualCheck = async () => {
    setCheckingUpdate(true);
    triggerHaptic("medium");
    try {
      const info = await checkForUpdate(CURRENT_APP_VERSION);
      if (info && info.hasUpdate) {
        toast({
          title: "Pembaruan Ditemukan!",
          description: `Versi ${info.latestVersion} siap dipasang.`,
          type: "success",
        });
        if (onUpdateAvailable) {
          onUpdateAvailable(info);
        }
      } else {
        toast({
          title: "Sudah Versi Terbaru",
          description: `Aplikasi Anda (v${CURRENT_APP_VERSION}) adalah versi paling mutakhir.`,
          type: "info",
        });
      }
    } catch {
      toast({
        title: "Gagal memeriksa pembaruan",
        description: "Periksa koneksi internet Anda.",
        type: "error",
      });
    } finally {
      setCheckingUpdate(false);
    }
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
            Pilih server cadangan jika salah satu server mengalami limitasi.
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

      {/* Auto-Update & Version Manager */}
      <Card className="border-border/70 bg-card/90">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-400" />
              <span>Pembaruan Aplikasi</span>
            </div>
            <Badge variant="outline" className="text-[10px] font-semibold text-emerald-400 border-emerald-500/40">
              <CheckCircle2 className="h-3 w-3 mr-1 inline" /> In-Place Update
            </Badge>
          </CardTitle>
          <CardDescription>
            Update langsung di dalam aplikasi tanpa perlu instal ulang atau hapus APK sebelumnya.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium text-white">Cek Otomatis Saat Buka</span>
              <p className="text-xs text-muted-foreground">Cek rilis terbaru setiap aplikasi dibuka</p>
            </div>
            <button
              onClick={toggleAutoCheckUpdate}
              className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors duration-200 ${
                autoCheckUpdate ? "bg-primary" : "bg-secondary"
              }`}
            >
              <div
                className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-200 ${
                  autoCheckUpdate ? "translate-x-6" : "translate-x-0"
                }`}
              />
            </button>
          </div>

          <div className="pt-2">
            <Button
              onClick={handleManualCheck}
              disabled={checkingUpdate}
              className="w-full bg-secondary hover:bg-secondary/80 border border-border text-foreground text-xs font-medium h-9 flex items-center justify-center gap-2"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${checkingUpdate ? "animate-spin text-purple-400" : ""}`} />
              <span>{checkingUpdate ? "Memeriksa ke GitHub..." : "Periksa Pembaruan Sekarang"}</span>
            </Button>
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
              <p className="text-xs text-muted-foreground">Getar pada klik tombol dan unduhan selesai</p>
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
              v{CURRENT_APP_VERSION} (shadcn/ui edition)
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
