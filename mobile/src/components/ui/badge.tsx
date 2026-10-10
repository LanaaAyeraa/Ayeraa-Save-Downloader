import * as React from "react";
import { cn } from "../../lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?:
    | "default"
    | "secondary"
    | "destructive"
    | "outline"
    | "success"
    | "platform"
    | "tiktok"
    | "instagram"
    | "youtube"
    | "spotify"
    | "twitter";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variantClasses = {
    default:
      "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
    secondary:
      "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
    destructive:
      "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
    outline: "text-foreground border-border",
    success:
      "border-transparent bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
    platform:
      "border-transparent bg-purple-500/20 text-purple-300 border border-purple-500/30",
    tiktok:
      "border-transparent bg-cyan-500/15 text-cyan-400 border border-cyan-500/30",
    instagram:
      "border-transparent bg-gradient-to-r from-amber-500/20 via-pink-500/20 to-purple-500/20 text-pink-400 border border-pink-500/30",
    youtube:
      "border-transparent bg-red-500/15 text-red-400 border border-red-500/30",
    spotify:
      "border-transparent bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
    twitter:
      "border-transparent bg-sky-500/15 text-sky-400 border border-sky-500/30",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge };
