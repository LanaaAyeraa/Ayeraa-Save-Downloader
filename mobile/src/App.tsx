import { useState, useEffect } from "react";
import { ToastProvider } from "./components/ui/toast";
import { Header } from "./components/Header";
import { DownloaderView } from "./components/DownloaderView";
import { HistoryView } from "./components/HistoryView";
import { SettingsView } from "./components/SettingsView";
import { BottomNav } from "./components/BottomNav";
import { UpdateDialog } from "./components/UpdateDialog";
import {
  checkForUpdate,
  isVersionIgnored,
  type UpdateInfo,
} from "./services/updaterService";

export function AppContent() {
  const [activeTab, setActiveTab] = useState<"downloader" | "history" | "settings">(
    "downloader"
  );
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);

  useEffect(() => {
    const autoCheck = localStorage.getItem("ayeraa_auto_check_update") !== "false";
    if (autoCheck) {
      // Delay slightly so initial UI renders immediately
      const timer = setTimeout(async () => {
        try {
          const info = await checkForUpdate();
          if (info && info.hasUpdate && !isVersionIgnored(info.latestVersion)) {
            setUpdateInfo(info);
            setIsUpdateDialogOpen(true);
          }
        } catch (e) {
          console.warn("Auto update check failed:", e);
        }
      }, 2500);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleManualCheckUpdate = (info: UpdateInfo) => {
    setUpdateInfo(info);
    setIsUpdateDialogOpen(true);
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-purple-500/20 selection:text-purple-300">
      {/* Background Gradient Mesh */}
      <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[500px] h-[350px] bg-purple-600/10 blur-[120px] rounded-full" />
        <div className="absolute top-1/3 -left-20 w-[300px] h-[300px] bg-pink-600/10 blur-[100px] rounded-full" />
        <div className="absolute bottom-20 -right-20 w-[350px] h-[350px] bg-indigo-600/10 blur-[120px] rounded-full" />
      </div>

      {/* Header */}
      <Header />

      {/* Main Container */}
      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-4">
        {activeTab === "downloader" && <DownloaderView />}
        {activeTab === "history" && <HistoryView />}
        {activeTab === "settings" && (
          <SettingsView onUpdateAvailable={handleManualCheckUpdate} />
        )}
      </main>

      {/* Fixed Bottom Navigation */}
      <BottomNav activeTab={activeTab} onChangeTab={setActiveTab} />

      {/* In-App Auto Update Dialog */}
      <UpdateDialog
        updateInfo={updateInfo}
        open={isUpdateDialogOpen}
        onClose={() => setIsUpdateDialogOpen(false)}
      />
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}
