import {
  Video,
  Camera,
  Play,
  Music2,
  Share2,
  Film,
  Image as ImageIcon,
  Layers,
  MessageCircle,
} from "lucide-react";

interface Platform {
  id: string;
  name: string;
  icon: any;
  color: string;
  gradient: string;
}

const PLATFORMS: Platform[] = [
  {
    id: "tiktok",
    name: "TikTok",
    icon: Video,
    color: "text-cyan-400",
    gradient: "from-cyan-500/20 to-pink-500/20 border-cyan-500/30",
  },
  {
    id: "instagram",
    name: "Instagram",
    icon: Camera,
    color: "text-pink-400",
    gradient: "from-amber-500/20 via-pink-500/20 to-purple-500/20 border-pink-500/30",
  },
  {
    id: "youtube",
    name: "YouTube",
    icon: Play,
    color: "text-red-400",
    gradient: "from-red-500/20 to-rose-600/20 border-red-500/30",
  },
  {
    id: "spotify",
    name: "Spotify",
    icon: Music2,
    color: "text-emerald-400",
    gradient: "from-emerald-500/20 to-green-600/20 border-emerald-500/30",
  },
  {
    id: "twitter",
    name: "X / Twitter",
    icon: MessageCircle,
    color: "text-sky-400",
    gradient: "from-sky-500/20 to-blue-600/20 border-sky-500/30",
  },
  {
    id: "facebook",
    name: "Facebook",
    icon: Share2,
    color: "text-blue-400",
    gradient: "from-blue-600/20 to-indigo-600/20 border-blue-500/30",
  },
  {
    id: "pinterest",
    name: "Pinterest",
    icon: ImageIcon,
    color: "text-red-400",
    gradient: "from-rose-500/20 to-red-500/20 border-rose-500/30",
  },
  {
    id: "douyin",
    name: "Douyin",
    icon: Film,
    color: "text-purple-400",
    gradient: "from-purple-500/20 to-indigo-500/20 border-purple-500/30",
  },
  {
    id: "all",
    name: "+10 More",
    icon: Layers,
    color: "text-purple-300",
    gradient: "from-purple-900/40 to-indigo-900/40 border-purple-500/20",
  },
];

interface PlatformBarProps {
  activePlatform?: string;
}

export function PlatformBar({ activePlatform }: PlatformBarProps) {
  return (
    <div className="w-full overflow-x-auto no-scrollbar py-1">
      <div className="flex items-center gap-2 px-1 min-w-max">
        {PLATFORMS.map((p) => {
          const Icon = p.icon;
          const isActive = activePlatform === p.id;
          return (
            <div
              key={p.id}
              className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold backdrop-blur-md transition-all duration-300 ${
                isActive
                  ? "bg-primary text-primary-foreground border-primary shadow-lg shadow-purple-600/30 scale-105"
                  : `bg-secondary/40 hover:bg-secondary/70 border-border/60 ${p.color}`
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{p.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
