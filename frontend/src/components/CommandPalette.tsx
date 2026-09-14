import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUIStore } from "../stores/ui";

const COMMANDS: { command: string; label: string; route: string }[] = [
  { command: "/search", label: "GLOBAL SEARCH", route: "/search" },
  { command: "/messages", label: "MESSAGING", route: "/messages" },
  { command: "/files", label: "FILE MANAGER", route: "/files" },
  { command: "/profile", label: "YOUR PROFILE", route: "/profile" },
  { command: "/settings", label: "SETTINGS", route: "/settings" },
  { command: "/upload", label: "UPLOAD FILE", route: "/files?action=upload" },
  { command: "/notifications", label: "NOTIFICATIONS", route: "/notifications" },
  { command: "/security", label: "SECURITY CENTER", route: "/security" },
  { command: "/vault", label: "DIGITAL VAULT", route: "/vault" },
  { command: "/communities", label: "COMMUNITIES", route: "/communities" },
  { command: "/feed", label: "SOCIAL FEED", route: "/feed" },
  { command: "/dashboard", label: "DASHBOARD", route: "/dashboard" },
];

export function CommandPalette() {
  const open = useUIStore((s) => s.commandPaletteOpen);
  const setOpen = useUIStore((s) => s.setCommandPalette);
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setQuery("");
        setOpen(!useUIStore.getState().commandPaletteOpen);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setOpen]);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return COMMANDS;
    return COMMANDS.filter(
      (c) => c.command.includes(q) || c.label.toLowerCase().includes(q)
    );
  }, [query]);

  if (!open) return null;

  const run = (route: string) => {
    setOpen(false);
    navigate(route);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/70 pt-[15vh] px-4"
      onClick={() => setOpen(false)}
      role="dialog"
      aria-modal="true"
      aria-label="Command center"
    >
      <div
        className="w-full max-w-xl terminal-card rounded-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="px-4 py-3 border-b border-borderline font-mono text-sm text-secondary">
          NEXUS COMMAND CENTER <span className="text-muted">// CTRL+K</span>
        </header>
        <div className="p-3">
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="> SEARCH: TYPE A COMMAND..."
            className="w-full bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-sm text-primary placeholder:text-muted focus:border-primary outline-none"
          />
          <ul className="mt-2 max-h-72 overflow-y-auto">
            {results.map((c) => (
              <li key={c.command}>
                <button
                  onClick={() => run(c.route)}
                  className="w-full flex items-center justify-between px-3 py-2 rounded hover:bg-panel2 text-left"
                >
                  <span className="font-mono text-sm text-secondary">{c.command}</span>
                  <span className="font-mono text-xs text-muted">{c.label}</span>
                </button>
              </li>
            ))}
            {results.length === 0 && (
              <li className="px-3 py-2 font-mono text-xs text-danger">NO MATCHING COMMANDS</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}