import { useState, useEffect } from "react";
import {
  History,
  Trash2,
  Share2,
  Film,
  Music,
  Image as ImageIcon,
} from "lucide-react";
import { Share } from "@capacitor/share";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { useToast } from "./ui/toast";
import {
  getHistory,
  clearHistory,
  deleteHistoryItem,
  triggerHaptic,
  type HistoryItem,
} from "../services/downloadManager";

export function HistoryView() {
  const { toast } = useToast();
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);

  useEffect(() => {
    setHistoryItems(getHistory());
  }, []);

  const handleClear = () => {
    if (confirm("Are you sure you want to clear your download history?")) {
      clearHistory();
      setHistoryItems([]);
      triggerHaptic("medium");
      toast({ title: "History cleared", type: "info" });
    }
  };

  const handleDelete = (id: string) => {
    deleteHistoryItem(id);
    setHistoryItems((prev) => prev.filter((i) => i.id !== id));
    triggerHaptic("medium");
  };

  const handleShare = async (item: HistoryItem) => {
    try {
      await Share.share({
        title: item.title,
        text: `Ayeraa Save Downloader: ${item.title}`,
        url: item.url,
      });
    } catch {
      // fallback
    }
  };

  if (historyItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-secondary/60 border border-border/60 text-muted-foreground mb-4">
          <History className="h-8 w-8" />
        </div>
        <h3 className="text-base font-semibold text-white">No Downloads Yet</h3>
        <p className="text-xs text-muted-foreground max-w-xs mt-1">
          Downloaded videos, songs, and photos will appear here for quick access.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 pb-24">
      {/* Header action */}
      <div className="flex items-center justify-between px-1">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Recent Downloads ({historyItems.length})
        </span>
        <Button
          size="sm"
          variant="ghost"
          onClick={handleClear}
          className="text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-950/30 h-8"
        >
          <Trash2 className="h-3.5 w-3.5 mr-1.5" />
          <span>Clear All</span>
        </Button>
      </div>

      {/* List */}
      <div className="space-y-2.5">
        {historyItems.map((item) => {
          const isAudio =
            item.type.toUpperCase().includes("MP3") ||
            item.type.toUpperCase().includes("AUDIO");
          const isPhoto =
            item.type.toUpperCase().includes("PHOTO") ||
            item.type.toUpperCase().includes("IMAGE");

          return (
            <Card
              key={item.id}
              className="border-border/60 bg-card/80 hover:bg-card/95 transition-all duration-200"
            >
              <CardContent className="p-3 sm:p-4 flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
                      isAudio
                        ? "bg-emerald-500/20 text-emerald-400"
                        : isPhoto
                        ? "bg-amber-500/20 text-amber-400"
                        : "bg-purple-500/20 text-purple-400"
                    }`}
                  >
                    {isAudio ? (
                      <Music className="h-5 w-5" />
                    ) : isPhoto ? (
                      <ImageIcon className="h-5 w-5" />
                    ) : (
                      <Film className="h-5 w-5" />
                    )}
                  </div>

                  <div className="truncate">
                    <h4 className="text-xs sm:text-sm font-semibold text-white truncate">
                      {item.title}
                    </h4>
                    <div className="flex items-center gap-2 mt-0.5">
                      <Badge variant="outline" className="text-[10px] py-0 px-1.5">
                        {item.type}
                      </Badge>
                      <span className="text-[10px] text-muted-foreground">
                        {new Date(item.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-1 shrink-0">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleShare(item)}
                    className="h-8 w-8 p-0 rounded-lg text-muted-foreground hover:text-white"
                  >
                    <Share2 className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDelete(item.id)}
                    className="h-8 w-8 p-0 rounded-lg text-muted-foreground hover:text-rose-400"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
