import { Download, Sparkles, ShieldCheck } from "lucide-react";
import { Badge } from "./ui/badge";

export function Header() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl px-4 py-3 sm:px-6">
      <div className="mx-auto flex max-w-md items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-pink-500 shadow-md shadow-purple-600/30">
            <Download className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="text-base font-bold tracking-tight text-white">
                Ayeraa Save
              </h1>
              <Sparkles className="h-3.5 w-3.5 text-pink-400" />
            </div>
            <p className="text-[11px] font-medium text-muted-foreground">
              Universal Media Downloader
            </p>
          </div>
        </div>

        {/* Right Badges */}
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className="border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-[11px] font-semibold py-0.5 px-2 gap-1"
          >
            <ShieldCheck className="h-3 w-3" />
            <span>v4.4 Pro</span>
          </Badge>
        </div>
      </div>
    </header>
  );
}
