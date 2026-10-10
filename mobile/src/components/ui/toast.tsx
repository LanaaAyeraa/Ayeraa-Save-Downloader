import React, { createContext, useContext, useState, useCallback } from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";
import { cn } from "../../lib/utils";

interface Toast {
  id: string;
  title: string;
  description?: string;
  type?: "default" | "success" | "error" | "info";
}

interface ToastContextType {
  toast: (opts: Omit<Toast, "id">) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback(({ title, description, type = "default" }: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, title, description, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      {/* Toast container */}
      <div className="fixed bottom-20 sm:bottom-6 right-0 left-0 sm:left-auto sm:right-6 z-50 flex flex-col gap-2 p-4 pointer-events-none sm:max-w-md items-center sm:items-end">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cn(
              "pointer-events-auto flex items-center justify-between gap-3 w-full max-w-sm rounded-xl p-4 shadow-xl backdrop-blur-md border transition-all animate-in slide-in-from-bottom-2",
              t.type === "success" && "bg-emerald-950/90 border-emerald-500/40 text-emerald-100",
              t.type === "error" && "bg-rose-950/90 border-rose-500/40 text-rose-100",
              t.type === "info" && "bg-sky-950/90 border-sky-500/40 text-sky-100",
              (!t.type || t.type === "default") && "bg-card/95 border-border text-foreground"
            )}
          >
            <div className="flex items-center gap-3">
              {t.type === "success" && <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />}
              {t.type === "error" && <AlertCircle className="h-5 w-5 text-rose-400 shrink-0" />}
              {t.type === "info" && <Info className="h-5 w-5 text-sky-400 shrink-0" />}
              <div className="flex flex-col">
                <span className="text-sm font-semibold">{t.title}</span>
                {t.description && <span className="text-xs opacity-80">{t.description}</span>}
              </div>
            </div>
            <button
              onClick={() => dismiss(t.id)}
              className="rounded-full p-1 opacity-60 hover:opacity-100 transition-opacity"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
