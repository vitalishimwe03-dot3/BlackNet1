import { useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { messages } from "../services/endpoints";
import { connectConversation, type WSHandle } from "../services/websocket";
import { useAuthStore } from "../stores/auth";
import { PageHeader } from "../components/PageLoader";
import { Avatar } from "../components/Avatar";
import { clockTime } from "../utils/format";
import type { Message } from "../types";

export function ConversationPage() {
  const { id } = useParams<{ id: string }>();
  const me = useAuthStore((s) => s.user)!;
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState("");
  const [typingUser, setTypingUser] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WSHandle | null>(null);

  const { data } = useQuery({
    queryKey: ["messages", id],
    queryFn: () => messages.history(id!, { page_size: 50 }).then((r) => r.data),
  });

  useEffect(() => {
    if (!id) return;
    const handle = connectConversation(id, (msg) => {
      const event = (msg as { event: string }).event;
      const payload = (msg as { payload: unknown }).payload as Message;
      if (event === "message.new" || event === "message.update") {
        queryClient.setQueryData<{ results: Message[] }>(["messages", id], (old) => {
          const results = old?.results ?? [];
          const existing = results.some((m) => m.id === payload.id);
          return { results: existing ? results.map((m) => (m.id === payload.id ? payload : m)) : [...results, payload] };
        });
      }
      if (event === "typing") {
        const p = (msg as { payload: { user: string; typing: boolean } }).payload;
        setTypingUser(p.typing ? p.user : null);
        if (p.typing) setTimeout(() => setTypingUser(null), 2500);
      }
    });
    wsRef.current = handle;
    return () => handle.close();
  }, [id, queryClient]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [data?.results.length, typingUser]);

  const send = () => {
    if (!draft.trim()) return;
    wsRef.current?.send("message.send", { content: draft.trim() });
    setDraft("");
  };

  const items = data?.results ?? [];

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-160px)]">
      <PageHeader
        title={`CHANNEL://${id?.slice(0, 5).toUpperCase() ?? "PRIVATE"}`}
        subtitle={`${items.length} MESSAGES ON RECORD`}
        action={<Link to="/messages" className="font-mono text-xs text-secondary hover:underline">← ALL CHANNELS</Link>}
      />

      <div className="terminal-card flex-1 rounded-lg overflow-hidden flex flex-col min-h-0">
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {items.map((m) => {
            const isMine = m.sender?.id === me.id;
            return (
              <div key={m.id} className={`flex ${isMine ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] ${isMine ? "bg-primary/10 border-primary/30" : "bg-panel2 border-borderline"} border rounded-lg px-3 py-2`}>
                  {!isMine && (
                    <div className="flex items-center gap-2 mb-1">
                      <Avatar username={m.sender?.username ?? "?"} avatar={m.sender?.avatar} size="sm" />
                      <span className="font-mono text-[10px] text-secondary">@{m.sender?.username}</span>
                    </div>
                  )}
                  {m.reply_preview && (
                    <div className="mb-1 border-l-2 border-muted pl-2 font-mono text-[10px] text-muted truncate">
                      REPLIES TO: {m.reply_preview}
                    </div>
                  )}
                  <p className="font-mono text-xs text-gray-200 whitespace-pre-wrap">{m.content}</p>
                  <div className="mt-1 flex justify-end gap-2 font-mono text-[9px] text-muted">
                    <span>{clockTime(m.created_at)}</span>
                    {m.is_edited && <span>[EDITED]</span>}
                    {isMine && m.read_by.filter((r) => r !== me.id).length > 0 && <span>[READ]</span>}
                  </div>
                  {Object.keys(m.reactions ?? {}).length > 0 && (
                    <div className="mt-1 flex gap-1">
                      {Object.values(m.reactions).map((r, i) => (
                        <span key={i} className="border border-borderline rounded-full px-1.5 text-xs">{r}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          <div ref={bottomRef} />
        </div>

        {typingUser && (
          <div className="px-4 py-1 font-mono text-[10px] text-secondary blink">@{typingUser} IS TYPING...</div>
        )}

        <div className="border-t border-borderline p-3 flex gap-2">
          <input
            value={draft}
            onChange={(e) => {
              setDraft(e.target.value);
              wsRef.current?.send("typing", { typing: e.target.value.length > 0 });
            }}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="> TRANSMIT MESSAGE..."
            className="flex-1 bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-xs text-primary placeholder:text-muted/50 focus:border-primary outline-none"
          />
          <button
            onClick={send}
            disabled={!draft.trim()}
            className="border border-primary/40 text-primary rounded px-4 font-mono text-xs hover:bg-primary/10 disabled:opacity-40"
          >
            SEND
          </button>
        </div>
      </div>
    </div>
  );
}