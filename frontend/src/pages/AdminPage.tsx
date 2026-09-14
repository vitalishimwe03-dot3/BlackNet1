import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import { PageHeader } from "../components/PageLoader";
import { TerminalCard } from "../components/TerminalCard";

export function AdminPage() {
  const { data: reports = [], isLoading: reportsLoading } = useQuery({
    queryKey: ["admin", "reports"],
    queryFn: () => api.get("/moderation/queue", { params: { page_size: 50 } }).then((r) => r.data),
  });

  const { data: audit = [] } = useQuery({
    queryKey: ["admin", "audit"],
    queryFn: () => api.get("/moderation/audit", { params: { page_size: 30 } }).then((r) => r.data),
  });

  const reportsList = reports.results ?? [];

  return (
    <div className="max-w-5xl mx-auto">
      <PageHeader title="ADMIN DASHBOARD" subtitle="MODERATION QUEUE // AUDIT TRAIL // PLATFORM HEALTH" />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TerminalCard title="MODERATION QUEUE" accent="warn" action={<span className="font-mono text-[10px] text-muted">{reportsList.length} OPEN</span>}>
          {reportsLoading ? (
            <div className="font-mono text-xs text-muted blink">LOADING...</div>
          ) : reportsList.length === 0 ? (
            <div className="font-mono text-xs text-muted">QUEUE CLEAR</div>
          ) : (
            <ul className="space-y-3">
              {reportsList.map((r: { id: string; target_type: string; target_id: string; category: string; status: string; reporter: string; created_at: string; reason: string }) => (
                <li key={r.id} className="border border-borderline rounded p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-xs text-danger">{r.category.toUpperCase()}</span>
                    <span className="font-mono text-[10px] text-muted">{r.status}</span>
                  </div>
                  <div className="mt-1 font-mono text-[10px] text-muted">
                    {r.target_type.toUpperCase()}::{r.target_id.slice(0, 8)} · REPORTED BY @{r.reporter}
                  </div>
                  {r.reason && <div className="mt-1 font-mono text-[10px] text-gray-300">{r.reason}</div>}
                </li>
              ))}
            </ul>
          )}
        </TerminalCard>

        <TerminalCard title="AUDIT TRAIL" accent="cyan">
          <ul className="space-y-2">
            {(audit.results ?? []).map((e: { id: string; action: string; created_at: string; user?: string | null }) => (
              <li key={e.id} className="flex justify-between font-mono text-[11px]">
                <span className="text-secondary">{e.action}</span>
                <span className="text-muted">{e.user || "SYSTEM"} · {new Date(e.created_at).toLocaleString()}</span>
              </li>
            ))}
            {(audit.results ?? []).length === 0 && <li className="font-mono text-xs text-muted">NO AUDIT EVENTS</li>}
          </ul>
        </TerminalCard>
      </div>

      <TerminalCard title="PLATFORM HEALTH" accent="primary" className="mt-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-xs">
          {[
            ["API", "ONLINE"],
            ["DATABASE", "ONLINE"],
            ["REDIS", "ONLINE"],
            ["WORKER", "ACTIVE"],
          ].map(([k, v]) => (
            <div key={k} className="border border-borderline rounded p-3 text-center">
              <div className="text-muted">{k}</div>
              <div className="text-primary mt-1">{v}</div>
            </div>
          ))}
        </div>
        <p className="mt-4 font-mono text-[10px] text-muted">
          FULL USER/STORAGE MANAGEMENT IS AVAILABLE IN /admin (DJANGO ADMIN).
        </p>
      </TerminalCard>
    </div>
  );
}