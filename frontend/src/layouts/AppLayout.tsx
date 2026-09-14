import { NavLink, Outlet, useNavigate } from "react-router-dom";
import clsx from "clsx";
import { useEffect } from "react";
import { useAuthStore } from "../stores/auth";
import { useUIStore } from "../stores/ui";
import { CommandPalette } from "../components/CommandPalette";
import { Avatar } from "../components/Avatar";
import { StatusDot } from "../components/StatusDot";
import { useNotificationsSocket } from "../hooks/useNotificationsSocket";

const NAV: { to: string; label: string; icon: string }[] = [
  { to: "/dashboard", label: "DASHBOARD", icon: "◈" },
  { to: "/feed", label: "FEED", icon: "▤" },
  { to: "/messages", label: "MESSAGES", icon: "✉" },
  { to: "/files", label: "FILES", icon: "▤▤" },
  { to: "/vault", label: "VAULT", icon: "◉" },
  { to: "/communities", label: "COMMUNITIES", icon: "◫" },
  { to: "/notifications", label: "NOTIFICATIONS", icon: "◔" },
  { to: "/security", label: "SECURITY", icon: "◈" },
  { to: "/settings", label: "SETTINGS", icon: "⚙" },
];

const MOBILE_NAV: { to: string; label: string; icon: string }[] = [
  { to: "/dashboard", label: "HOME", icon: "◈" },
  { to: "/feed", label: "FEED", icon: "▤" },
  { to: "/messages", label: "MSG", icon: "✉" },
  { to: "/files", label: "FILES", icon: "▤▤" },
  { to: "/communities", label: "COMMS", icon: "◫" },
];

export function AppLayout() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const sidebarOpen = useUIStore((s) => s.sidebarOpen);
  const navigate = useNavigate();
  useNotificationsSocket();

  useEffect(() => {
    if (!user) navigate("/login");
  }, [user, navigate]);

  if (!user) return null;

  return (
    <div className="flex h-screen overflow-hidden bg-bg text-gray-200">
      <CommandPalette />

      {/* Sidebar (desktop) */}
      <aside
        className={clsx(
          "hidden lg:flex flex-col w-60 shrink-0 border-r border-borderline bg-panel/60 transition-all",
          sidebarOpen ? "lg:flex" : "lg:hidden"
        )}
      >
        <div className="flex items-center gap-2 px-4 py-4 border-b border-borderline">
          <span className="text-primary text-xl font-mono glow-text">◈</span>
          <div>
            <div className="font-mono text-sm text-primary tracking-wide">BLACKNET</div>
            <div className="font-mono text-[10px] text-muted">NEXUS://PRIVATE</div>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto py-3">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 px-4 py-2.5 font-mono text-sm tracking-wide transition-colors",
                  isActive
                    ? "text-primary bg-primary/10 border-l-2 border-primary glow-text"
                    : "text-muted hover:text-primary hover:bg-panel2/50 border-l-2 border-transparent"
                )
              }
            >
              <span className="w-4 text-center">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-3 border-t border-borderline">
          <button
            onClick={() => navigate("/profile/" + user.username)}
            className="flex w-full items-center gap-3 rounded hover:bg-panel2 p-1"
          >
            <Avatar username={user.username} avatar={user.avatar} size="sm" online={user.is_online} />
            <div className="text-left leading-tight">
              <div className="font-mono text-xs text-primary">@{user.username}</div>
              <div className="font-mono text-[10px] text-muted">STORAGE {user.storage_bytes_total > 0 ? Math.round((user.storage_bytes_used / user.storage_bytes_total) * 100) : 0}%</div>
            </div>
          </button>
          <button
            onClick={async () => {
              await logout();
              navigate("/");
            }}
            className="mt-2 w-full text-left font-mono text-xs text-muted hover:text-danger"
          >
            [ DISCONNECT ]
          </button>
        </div>
      </aside>

      {/* Main column */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-borderline bg-panel/40">
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden font-mono text-primary"
              onClick={() => useUIStore.getState().toggleSidebar()}
              aria-label="Toggle navigation"
            >
              ☰
            </button>
            <div className="hidden md:flex items-center gap-2">
              <StatusDot online pulse={false} />
              <span className="font-mono text-[10px] text-muted">[SYSTEM] CONNECTION ESTABLISHED</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="font-mono text-[10px] text-muted hidden sm:inline">
              USER: <span className="text-primary">{user.username.toUpperCase()}</span>
            </span>
            <button
              className="font-mono text-xs text-secondary border border-secondary/40 rounded px-2 py-1 hover:bg-secondary/10"
              onClick={() => useUIStore.getState().setCommandPalette(true)}
            >
              ⌘K
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>

        {/* Mobile bottom nav */}
        <nav className="lg:hidden flex items-center justify-around border-t border-borderline bg-panel/80 py-2">
          {MOBILE_NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                clsx(
                  "flex flex-col items-center gap-0.5 font-mono text-[10px] px-2",
                  isActive ? "text-primary glow-text" : "text-muted"
                )
              }
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}