import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../stores/auth";
import { files as filesApi, posts as postsApi, notifications as notifApi, messages as msgApi } from "../services/endpoints";
import { TerminalCard } from "../components/TerminalCard";
import { ProgressBar } from "../components/ProgressBar";
import { PageHeader } from "../components/PageLoader";
import { NeonButton } from "../components/NeonButton";
import { Avatar } from "../components/Avatar";
import { formatBytes, formatStorage, timeAgo } from "../utils/format";

export function DashboardPage() {
  const user = useAuthStore((s) => s.user)!;
  const navigate = useNavigate();

  const { data: usage } = useQuery({ queryKey: ["storage"], queryFn: () => filesApi.usage().then((r) => r.data) });
  const { data: myPosts } = useQuery({ queryKey: ["posts", "mine"], queryFn: () => postsApi.list().then((r) => r.data) });
  const { data: convos } = useQuery({ queryKey: ["conversations"], queryFn: () => msgApi.list().then((r) => r.data) });
  const { data: notifs } = useQuery({ queryKey: ["notifications"], queryFn: () => notifApi.list({ page_size: 5 }).then((r) => r.data) });
  const { data: recentFiles } = useQuery({ queryKey: ["files", "recent"], queryFn: () => filesApi.list({ page_size: 5 }).then((r) => r.data) });

  const used = user.storage_bytes_used;
  const total = user.storage_bytes_total;
  const percent = total ? (used / total) * 100 : 0;

  const segments = usage
    ? [
        { label: "IMG", value: (usage.image_bytes / total) * 100 || 0, color: "#00D9FF" },
        { label: "VID", value: (usage.video_bytes / total) * 100 || 0, color: "#FFB000" },
        { label: "DOC", value: (usage.document_bytes / total) * 100 || 0, color: "#00FF88" },
      ]
    : undefined;

  return (
    <div className="max-w-6xl mx-auto">
      <PageHeader
        title={`ACCESS GRANTED // USER: ${user.username.toUpperCase()}`}
        subtitle={`REPUTATION // ${Math.max(0, Math.floor((user.storage_bytes_used / 1024 / 1024) + Math.floor((user.created_at ? Date.now() - new Date(user.created_at).getTime() : 0) / 86400000)))}`}
      />

      {/* Quick actions */}
      <div className="flex flex-wrap gap-2 mb-6">
        <NeonButton onClick={() => navigate("/files?action=upload")}>▲ QUICK UPLOAD</NeonButton>
        <NeonButton variant="cyan" onClick={() => navigate("/messages")}>
          ✉ QUICK MESSAGE
        </NeonButton>
        <NeonButton variant="ghost" onClick={() => navigate("/feed")}>
          + CREATE POST
        </NeonButton>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Storage meter */}
        <TerminalCard
          title="STORAGE"
          accent="primary"
          action={<span className="font-mono text-[10px] text-muted">USED {formatStorage(used)} / {formatStorage(total)}</span>}
        >
          <ProgressBar percent={percent} segments={segments} accent="primary" />
          <div className="mt-3 grid grid-cols-3 gap-2 font-mono text-[11px]">
            <div>
              <div className="text-muted">USED</div>
              <div className="text-primary">{formatBytes(used)}</div>
            </div>
            <div>
              <div className="text-muted">FREE</div>
              <div className="text-secondary">{formatBytes(Math.max(0, total - used))}</div>
            </div>
            <div>
              <div className="text-muted">TOTAL</div>
              <div className="text-warn">{formatBytes(total)}</div>
            </div>
          </div>
        </TerminalCard>

        {/* System status */}
        <TerminalCard title="SYSTEM STATUS" accent="cyan">
          <ul className="font-mono text-xs space-y-2 text-muted">
            <li className="flex justify-between"><span>NETWORK</span><span className="text-primary">ONLINE</span></li>
            <li className="flex justify-between"><span>MESSAGING</span><span className="text-primary">ONLINE</span></li>
            <li className="flex justify-between"><span>STORAGE</span><span className="text-primary">ONLINE</span></li>
            <li className="flex justify-between"><span>FILE PROCESSING</span><span className="text-secondary">ACTIVE</span></li>
            <li className="flex justify-between"><span>SESSION</span><span className="text-primary">SECURED</span></li>
            <li className="flex justify-between"><span>2FA</span><span className={user.is_2fa_enabled ? "text-primary" : "text-warn"}>{user.is_2fa_enabled ? "ENABLED" : "OFF"}</span></li>
          </ul>
        </TerminalCard>

        {/* Notifications */}
        <TerminalCard
          title="NOTIFICATIONS"
          accent="warn"
          action={<Link to="/notifications" className="font-mono text-[10px] text-secondary hover:underline">VIEW ALL</Link>}
        >
          <ul className="space-y-2">
            {(notifs?.results ?? []).slice(0, 4).map((n) => (
              <li key={n.id} className="font-mono text-[11px]">
                <span className="text-muted">[{new Date(n.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}]</span>{" "}
                <span className={n.is_read ? "text-muted" : "text-warn"}>{n.message}</span>
              </li>
            ))}
            {notifs?.results.length === 0 && <li className="font-mono text-xs text-muted">NO NOTIFICATIONS</li>}
          </ul>
        </TerminalCard>

        {/* Recent posts */}
        <TerminalCard
          title="RECENT POSTS"
          accent="primary"
          action={<Link to="/feed" className="font-mono text-[10px] text-secondary hover:underline">OPEN FEED</Link>}
        >
          <ul className="space-y-2">
            {(myPosts?.results ?? []).slice(0, 4).map((p) => (
              <li key={p.id} className="font-mono text-[11px] text-muted truncate">
                <span className="text-primary">[{p.author.username.toUpperCase()}]</span> {p.content}
              </li>
            ))}
            {myPosts?.results.length === 0 && <li className="font-mono text-xs text-muted">NO TRANSMISSIONS YET</li>}
          </ul>
        </TerminalCard>

        {/* Recent files */}
        <TerminalCard
          title="RECENT FILES"
          accent="cyan"
          action={<Link to="/files" className="font-mono text-[10px] text-secondary hover:underline">OPEN FILES</Link>}
        >
          <ul className="space-y-2">
            {(recentFiles?.results ?? []).slice(0, 4).map((f) => (
              <li key={f.id} className="flex items-center justify-between font-mono text-[11px]">
                <span className="text-muted truncate max-w-[60%]">{f.original_name}</span>
                <span className="text-secondary">{formatBytes(f.size_bytes)}</span>
              </li>
            ))}
            {recentFiles?.results.length === 0 && <li className="font-mono text-xs text-muted">NO FILES YET</li>}
          </ul>
        </TerminalCard>

        {/* Online contacts / recent conversations */}
        <TerminalCard
          title="CONTACTS"
          accent="cyan"
          action={<Link to="/messages" className="font-mono text-[10px] text-secondary hover:underline">MESSAGES</Link>}
        >
          <ul className="space-y-2">
            {(convos?.results ?? []).slice(0, 4).map((c) => (
              <li key={c.id}>
                <Link to={`/messages/${c.id}`} className="flex items-center justify-between font-mono text-[11px] hover:text-primary">
                  <span className="flex items-center gap-2 text-muted">
                    <Avatar username={c.members[0]?.username ?? "?"} online={c.members[0]?.is_online} size="sm" />
                    {c.name || c.members.find((m) => m.id !== user.id)?.username || "CONVERSATION"}
                  </span>
                  <span className="text-muted/60">{timeAgo(c.last_message_at)}</span>
                </Link>
              </li>
            ))}
            {convos?.results.length === 0 && <li className="font-mono text-xs text-muted">NO CONVERSATIONS</li>}
          </ul>
        </TerminalCard>
      </div>
    </div>
  );
}