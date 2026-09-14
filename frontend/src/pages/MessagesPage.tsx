import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { messages } from "../services/endpoints";
import { useAuthStore } from "../stores/auth";
import { PageHeader, EmptyState } from "../components/PageLoader";
import { NeonButton } from "../components/NeonButton";
import { Avatar } from "../components/Avatar";
import { timeAgo } from "../utils/format";
import { StatusDot } from "../components/StatusDot";

export function MessagesPage() {
  const me = useAuthStore((s) => s.user)!;
  const queryClient = useQueryClient();
  const [username, setUsername] = useState("");
  const [groupUsers, setGroupUsers] = useState("");
  const [groupName, setGroupName] = useState("");

  const convos = useQuery({ queryKey: ["conversations"], queryFn: () => messages.list().then((r) => r.data) });

  const directMutation = useMutation({
    mutationFn: () => messages.direct(username.trim()),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["conversations"] }),
  });

  const groupMutation = useMutation({
    mutationFn: () => messages.group(groupName.trim() || "UNNAMED", groupUsers.split(",").map((s) => s.trim()).filter(Boolean)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["conversations"] }),
  });

  const list = convos.data?.results ?? [];

  return (
    <div className="max-w-3xl mx-auto">
      <PageHeader title="MESSAGING" subtitle="CHANNEL://PRIVATE — REAL-TIME CONVERSATIONS" />

      {/* Start new conversation */}
      <div className="terminal-card rounded-lg p-4 mb-6 space-y-3">
        <div className="flex gap-2">
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="OPEN DIRECT CHANNEL: @username"
            className="flex-1 bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-xs text-primary placeholder:text-muted/50 focus:border-primary outline-none"
          />
          <NeonButton size="sm" onClick={() => directMutation.mutate()} disabled={!username.trim()}>
            OPEN
          </NeonButton>
        </div>
        <div className="flex gap-2">
          <input
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            placeholder="GROUP NAME"
            className="w-32 bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-xs text-primary placeholder:text-muted/50 focus:border-primary outline-none"
          />
          <input
            value={groupUsers}
            onChange={(e) => setGroupUsers(e.target.value)}
            placeholder="MEMBERS: user1,user2"
            className="flex-1 bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-xs text-primary placeholder:text-muted/50 focus:border-primary outline-none"
          />
          <NeonButton size="sm" variant="cyan" onClick={() => groupMutation.mutate()} disabled={!groupUsers.trim()}>
            CREATE
          </NeonButton>
        </div>
      </div>

      {list.length === 0 ? (
        <EmptyState icon="✉" title="NO CONVERSATIONS" hint="OPEN A DIRECT CHANNEL ABOVE" />
      ) : (
        <ul className="space-y-2">
          {list.map((c) => {
            const other = c.members.find((m) => m.id !== me.id);
            const title = c.name || other?.username || "CONVERSATION";
            return (
              <li key={c.id}>
                <Link
                  to={`/messages/${c.id}`}
                  className="terminal-card rounded-lg p-3 flex items-center gap-3 hover:border-primary/40 transition-colors"
                >
                  <Avatar username={other?.username ?? title} avatar={other?.avatar} online={other?.is_online} />
                  <div className="flex-1 min-w-0">
                    <div className="font-mono text-sm text-primary truncate">{title.toUpperCase()}</div>
                    <div className="font-mono text-xs text-muted truncate">
                      {other ? <StatusDot online={other.is_online} pulse={false} /> : null} {c.last_message || "NO MESSAGES YET"}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="font-mono text-[10px] text-muted">{timeAgo(c.last_message_at)}</div>
                    {c.unread_count > 0 && (
                      <div className="mt-1 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1.5 font-mono text-[10px] text-bg">
                        {c.unread_count}
                      </div>
                    )}
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}