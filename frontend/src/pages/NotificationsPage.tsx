import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { notifications } from "../services/endpoints";
import { PageHeader, EmptyState } from "../components/PageLoader";
import { TerminalCard } from "../components/TerminalCard";
import { NeonButton } from "../components/NeonButton";
import { timeAgo } from "../utils/format";

export function NotificationsPage() {
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notifications.list({ page_size: 50 }).then((r) => r.data),
  });

  const readAllMutation = useMutation({
    mutationFn: () => notifications.readAll(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const readMutation = useMutation({
    mutationFn: (id: string) => notifications.markRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const list = data?.results ?? [];

  return (
    <div className="max-w-3xl mx-auto">
      <PageHeader
        title="NOTIFICATION CENTER"
        subtitle="REAL-TIME ALERTS FROM THE NEXUS"
        action={
          list.some((n) => !n.is_read) ? (
            <NeonButton size="sm" onClick={() => readAllMutation.mutate()}>
              MARK ALL READ
            </NeonButton>
          ) : undefined
        }
      />

      <TerminalCard title="INBOX // LIVE" accent="warn">
        {list.length === 0 ? (
          <EmptyState icon="◔" title="NO NOTIFICATIONS" hint="SYSTEM ALERTS APPEAR HERE IN REAL TIME" />
        ) : (
          <ul className="divide-y divide-borderline">
            {list.map((n) => (
              <li key={n.id} className="py-3 cursor-pointer" onClick={() => !n.is_read && readMutation.mutate(n.id)}>
                <div className="flex items-start gap-3">
                  <div className={`font-mono text-[10px] ${n.is_read ? "text-muted" : "text-warn"}`}>
                    [{new Date(n.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}]
                  </div>
                  <div className="flex-1">
                    <div className={`font-mono text-xs ${n.is_read ? "text-muted" : "text-gray-200"}`}>{n.message}</div>
                    {n.post_detail && (
                      <div className="mt-1 font-mono text-[10px] text-muted">POST: {n.post_detail.content}</div>
                    )}
                  </div>
                  <span className="font-mono text-[9px] text-muted shrink-0">{timeAgo(n.created_at)}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </TerminalCard>
    </div>
  );
}