import { useState } from "react";
import {
  Sparkles,
  Download,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import {
  type UpdateInfo,
  triggerApkInstallation,
  ignoreVersion,
} from "../services/updaterService";

interface UpdateDialogProps {
  updateInfo: UpdateInfo | null;
  open: boolean;
  onClose: () => void;
}

export function UpdateDialog({ updateInfo, open, onClose }: UpdateDialogProps) {
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [downloadedMB, setDownloadedMB] = useState(0);
  const [totalMB, setTotalMB] = useState(0);
  const [statusText, setStatusText] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!updateInfo) return null;

  const handleStartUpdate = async () => {
    setDownloading(true);
    setProgress(0);
    setErrorMsg(null);
    setStatusText("Menghubungkan ke server pembaruan...");

    try {
      const result = await triggerApkInstallation(
        updateInfo.apkUrl,
        (percent, loaded, total) => {
          setProgress(percent > 0 ? percent : 50);
          setDownloadedMB(Number((loaded / (1024 * 1024)).toFixed(1)));
          if (total > 0) {
            setTotalMB(Number((total / (1024 * 1024)).toFixed(1)));
          }
          setStatusText(`Mengunduh pembaruan... ${percent > 0 ? `${percent}%` : ""}`);
        }
      );

      if (!result.success) {
        setDownloading(false);
        setErrorMsg(
          result.error ||
            "Gagal memasang otomatis. Pastikan izin 'Install Unknown Apps' sudah diizinkan di Pengaturan HP Anda."
        );
      } else {
        setStatusText("Pembaruan siap! Membuka penginstal Android...");
      }
    } catch (err: any) {
      setDownloading(false);
      setErrorMsg(err.message || "Terjadi kesalahan saat mengunduh pembaruan.");
    }
  };

  const handleIgnore = () => {
    ignoreVersion(updateInfo.latestVersion);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent onClose={onClose} className="border-purple-500/30">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
              <Sparkles className="h-5 w-5" />
            </span>
            <DialogTitle>Pembaruan Tersedia!</DialogTitle>
          </div>
          <DialogDescription>
            Versi terbaru siap dipasang langsung tanpa perlu instal ulang atau hapus aplikasi.
          </DialogDescription>
        </DialogHeader>

        {/* Version Compare Cards */}
        <div className="flex items-center justify-between p-3 rounded-xl bg-secondary/50 border border-border/70 my-2">
          <div className="flex flex-col">
            <span className="text-[11px] text-muted-foreground uppercase font-medium">Versi Sekarang</span>
            <span className="text-sm font-semibold text-white">v{updateInfo.currentVersion}</span>
          </div>
          <ArrowRight className="h-4 w-4 text-muted-foreground" />
          <div className="flex flex-col items-end">
            <span className="text-[11px] text-muted-foreground uppercase font-medium">Versi Terbaru</span>
            <Badge variant="default" className="text-xs font-bold bg-purple-600 hover:bg-purple-500">
              {updateInfo.latestVersion}
            </Badge>
          </div>
        </div>

        {/* Changelog Card */}
        <div className="space-y-1.5 my-2">
          <span className="text-xs font-semibold text-white">Catatan Perubahan:</span>
          <div className="max-h-36 overflow-y-auto rounded-lg bg-black/40 border border-border/60 p-3 text-xs text-muted-foreground whitespace-pre-wrap leading-relaxed">
            {updateInfo.body || "Pembaruan stabilitas sistem, performa unduhan, dan perbaikan bug."}
          </div>
        </div>

        {/* Progress or Status */}
        {downloading && (
          <div className="space-y-2 my-2 p-3 rounded-xl bg-purple-950/20 border border-purple-800/30">
            <div className="flex justify-between text-xs font-medium text-purple-200">
              <span>{statusText}</span>
              {totalMB > 0 && (
                <span>
                  {downloadedMB} MB / {totalMB} MB
                </span>
              )}
            </div>
            <Progress value={progress} className="h-2" />
            <div className="flex items-center gap-1.5 text-[11px] text-purple-300/80">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Data dan riwayat unduhan Anda akan tetap aman.</span>
            </div>
          </div>
        )}

        {/* Error Feedback */}
        {errorMsg && (
          <div className="flex items-start gap-2 p-3 rounded-xl bg-destructive/10 border border-destructive/30 text-xs text-red-300 my-2">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-400" />
            <div>
              <p className="font-semibold">Info Pembaruan:</p>
              <p className="mt-0.5">{errorMsg}</p>
            </div>
          </div>
        )}

        <DialogFooter className="mt-4">
          {!downloading ? (
            <>
              <Button variant="ghost" onClick={handleIgnore} className="text-xs">
                Abaikan Versi Ini
              </Button>
              <Button
                variant="default"
                onClick={handleStartUpdate}
                className="bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                <span>Update Otomatis Sekarang</span>
              </Button>
            </>
          ) : (
            <div className="w-full flex items-center justify-center py-1 text-xs text-muted-foreground">
              <CheckCircle className="h-4 w-4 mr-1.5 text-emerald-400 animate-pulse" />
              <span>Proses unduhan sedang berjalan di latar belakang...</span>
            </div>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
