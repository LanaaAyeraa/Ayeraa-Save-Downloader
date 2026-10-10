import { useState } from "react";
import { ToastProvider } from "./components/ui/toast";
import { Header } from "./components/Header";
import { DownloaderView } from "./components/DownloaderView";
import { HistoryView } from "./components/HistoryView";
import { SettingsView } from "./components/SettingsView";
import { BottomNav } from "./components/BottomNav";

export function AppContent() {
  const [activeTab, setActiveTab] = useState<"downloader" | "history" | "settings">(
    "downloader"
  );

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
        {activeTab === "settings" && <SettingsView />}
      </main>

      {/* Fixed Bottom Navigation */}
      <BottomNav activeTab={activeTab} onChangeTab={setActiveTab} />
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
