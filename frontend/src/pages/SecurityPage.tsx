import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { security } from "../services/endpoints";
import { PageHeader } from "../components/PageLoader";
import { TerminalCard } from "../components/TerminalCard";
import { NeonButton } from "../components/NeonButton";
import { StatusDot } from "../components/StatusDot";
import { timeAgo } from "../utils/format";

export function SecurityPage() {
  const queryClient = useQueryClient();
  const [totpCode, setTotpCode] = useState("");
  const [twofaStatus, setTwofaStatus] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ["security"],
    queryFn: () => security.overview().then((r) => r.data),
  });

  const revokeMutation = useMutation({
    mutationFn: (id: string) => api.post(`/users/me/sessions/${id}/revoke`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["security"] }),
  });

  const setup2fa = async () => {
    // Enable needs the TOTP secret + QR setup; show a simplified flow.
    setTwofaStatus("GENERATING SECRET...");
    try {
      const { data: secret } = await api.post<{ secret: string; provisioning_uri: string }>("/auth/2fa/setup");
      setTwofaStatus(`SECRET: ${secret.secret} — ENTER A CODE TO CONFIRM`);
    } catch {
      setTwofaStatus("2FA ALREADY ENABLED OR FAILED");
    }
  };

  const verify2fa = async () => {
    try {
      await api.post("/auth/2fa/verify", { code: totpCode });
      setTwofaStatus("2FA ENABLED");
      queryClient.invalidateQueries({ queryKey: ["security"] });
      setTotpCode("");
    } catch {
      setTwofaStatus("INVALID CODE");
    }
  };

  const sessions = data?.sessions ?? [];

  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader title="SECURITY://CENTER" subtitle="SESSIONS, LOGIN HISTORY, 2FA AND ALERTS" />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TerminalCard title="ACTIVE SESSIONS" accent="cyan" action={<StatusDot online pulse={false} />}>
          <ul className="space-y-3">
            {sessions.map((s) => (
              <li key={s.id} className="flex items-center justify-between gap-2">
                <div className="min-w-0">
                  <div className="font-mono text-xs text-gray-200 truncate">
                    {s.device_name || s.user_agent.slice(0, 40)}
                    {s.is_current && <span className="text-primary ml-2">[CURRENT]</span>}
                  </div>
                  <div className="font-mono text-[10px] text-muted">
                    {s.ip_address || "UNKNOWN IP"} · {timeAgo(s.last_seen)}
                  </div>
                </div>
                {!s.is_current && (
                  <button
                    onClick={() => revokeMutation.mutate(s.id)}
                    className="font-mono text-[10px] text-danger hover:underline shrink-0"
                  >
                    REVOKE
                  </button>
                )}
              </li>
            ))}
            {sessions.length === 0 && <li className="font-mono text-xs text-muted">NO ACTIVE SESSIONS</li>}
          </ul>
        </TerminalCard>

        <TerminalCard title="2-FACTOR AUTHENTICATION" accent="primary">
          <div className="font-mono text-xs text-muted mb-3">
            STATUS:{" "}
            <span className={data?.two_factor_enabled ? "text-primary" : "text-warn"}>
              {data?.two_factor_enabled ? "ENABLED" : "DISABLED"}
            </span>
          </div>
          {!data?.two_factor_enabled ? (
            <>
              <NeonButton size="sm" variant="cyan" onClick={setup2fa}>
                SET UP TOTP
              </NeonButton>
              {twofaStatus && (
                <div className="mt-3 font-mono text-[10px] text-secondary break-all">{twofaStatus}</div>
              )}
              {twofaStatus?.includes("SECRET") && (
                <div className="mt-2 flex gap-2">
                  <input
                    value={totpCode}
                    onChange={(e) => setTotpCode(e.target.value)}
                    placeholder="6 DIGIT CODE"
                    className="bg-panel2 border border-borderline rounded px-2 py-1 font-mono text-xs text-primary outline-none focus:border-primary w-28"
                  />
                  <NeonButton size="sm" onClick={verify2fa}>
                    VERIFY
                  </NeonButton>
                </div>
              )}
            </>
          ) : (
            <p className="font-mono text-xs text-muted">TWO-FACTOR AUTH IS ACTIVE // YOUR ACCOUNT IS PROTECTED</p>
          )}
        </TerminalCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
        <TerminalCard title="LOGIN HISTORY" accent="warn">
          <ul className="space-y-2">
            {(data?.login_history ?? []).slice(0, 10).map((e, i) => (
              <li key={`${e.created_at}-${i}`} className="flex justify-between font-mono text-[11px]">
                <span className={e.event_type === "LOGIN_FAILED" ? "text-danger" : "text-muted"}>
                  {e.event_type}
                </span>
                <span className="text-muted/60">{e.ip_address || "-"} · {timeAgo(e.created_at)}</span>
              </li>
            ))}
            {(data?.login_history ?? []).length === 0 && <li className="font-mono text-xs text-muted">NO LOGIN EVENTS</li>}
          </ul>
        </TerminalCard>

        <TerminalCard title="THREAT METRICS" accent="danger">
          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div>
              <div className="text-muted">PASSWORD CHANGES</div>
              <div className="text-primary text-lg">{data?.password_changes ?? 0}</div>
            </div>
            <div>
              <div className="text-muted">SUSPICIOUS LOGINS</div>
              <div className="text-danger text-lg">{data?.suspicious_logins ?? 0}</div>
            </div>
            <div>
              <div className="text-muted">DEVICES</div>
              <div className="text-secondary text-lg">{data?.device_count ?? 0}</div>
            </div>
            <div>
              <div className="text-muted">PROTECTION</div>
              <div className={data?.two_factor_enabled ? "text-primary text-lg" : "text-warn text-lg"}>
                {data?.two_factor_enabled ? "ACTIVE" : "BASIC"}
              </div>
            </div>
          </div>
        </TerminalCard>
      </div>
    </div>
  );
}