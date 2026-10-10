import { Download, History, Settings } from "lucide-react";
import { triggerHaptic } from "../services/downloadManager";

interface BottomNavProps {
  activeTab: "downloader" | "history" | "settings";
  onChangeTab: (tab: "downloader" | "history" | "settings") => void;
}

export function BottomNav({ activeTab, onChangeTab }: BottomNavProps) {
  const tabs = [
    {
      id: "downloader" as const,
      label: "Downloader",
      icon: Download,
    },
    {
      id: "history" as const,
      label: "History",
      icon: History,
    },
    {
      id: "settings" as const,
      label: "Settings",
      icon: Settings,
    },
  ];

  const handleTabClick = (id: "downloader" | "history" | "settings") => {
    triggerHaptic("medium");
    onChangeTab(id);
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-border/50 bg-background/90 backdrop-blur-2xl py-2 px-6 safe-area-bottom">
      <div className="mx-auto flex max-w-md items-center justify-around">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={`flex flex-col items-center justify-center gap-1 py-1 px-4 rounded-xl transition-all duration-200 ${
                isActive
                  ? "text-primary scale-105"
                  : "text-muted-foreground hover:text-foreground active:scale-95"
              }`}
            >
              <div
                className={`flex h-8 w-12 items-center justify-center rounded-full transition-all duration-300 ${
                  isActive ? "bg-primary/20 text-pink-400" : ""
                }`}
              >
                <Icon className="h-5 w-5" />
              </div>
              <span
                className={`text-[11px] font-medium tracking-tight ${
                  isActive ? "text-white font-bold" : ""
                }`}
              >
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
