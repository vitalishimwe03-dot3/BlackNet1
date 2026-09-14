import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { auth } from "../services/endpoints";
import { api } from "../services/api";
import { useAuthStore } from "../stores/auth";
import { PageHeader } from "../components/PageLoader";
import { TerminalCard } from "../components/TerminalCard";
import { NeonButton } from "../components/NeonButton";
import { Avatar } from "../components/Avatar";
import { formatBytes, timeAgo } from "../utils/format";

export function ProfilePage() {
  const { username } = useParams<{ username: string }>();
  const me = useAuthStore((s) => s.user)!;
  const effective = username ?? me.username;
  const queryClient = useQueryClient();

  const { data: profile, isLoading } = useQuery({
    queryKey: ["users", effective],
    queryFn: () => auth.profile(effective).then((r) => r.data),
  });

  const followMutation = useMutation({
    mutationFn: () => api.post(`/users/${effective}/follow`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  if (isLoading) return <PageHeader title="LOADING PROFILE..." />;
  if (!profile) return <PageHeader title="PROFILE NOT FOUND" />;

  const isSelf = effective === me.username;

  return (
    <div className="max-w-3xl mx-auto">
      <PageHeader title={`PROFILE // ${effective.toUpperCase()}`} subtitle="USER://NEXUS" />

      <TerminalCard title="IDENTITY" accent="primary" action={<>{profile.is_online ? <span className="font-mono text-[10px] text-primary">ONLINE</span> : <span className="font-mono text-[10px] text-muted">OFFLINE</span>}</>}>
        <div className="flex flex-col sm:flex-row items-start gap-4">
          <Avatar username={effective} avatar={profile.avatar} size="xl" online={profile.is_online} />
          <div className="flex-1 min-w-0">
            <div className="font-mono text-base text-primary glow-text">@{effective}</div>
            <div className="font-mono text-xs text-muted mt-1">REGISTERED: {timeAgo(profile.created_at)}</div>
            <div className="font-mono text-xs text-muted">LAST ACTIVE: {timeAgo(profile.last_active)}</div>
            {profile.reputation_public !== false && (
              <div className="mt-3 font-mono text-sm text-secondary">
                REPUTATION // <span className="text-secondary glow-text-cyan">{Math.floor(500 + effective.length * 73)}</span>
              </div>
            )}
            <p className="mt-3 font-mono text-sm text-gray-300 whitespace-pre-wrap">{profile.bio || "NO BIO YET"}</p>
            {!isSelf && (
              <div className="mt-4">
                <NeonButton size="sm" variant="cyan" onClick={() => followMutation.mutate()}>
                  {followMutation.isPending ? "..." : "FOLLOW"}
                </NeonButton>
              </div>
            )}
            {isSelf && (
              <div className="mt-4 font-mono text-[10px] text-muted">
                YOUR STORAGE // USED {formatBytes(me.storage_bytes_used)} / {formatBytes(me.storage_bytes_total)}
              </div>
            )}
          </div>
        </div>
      </TerminalCard>

      <TerminalCard title="BADGES" accent="cyan" className="mt-4">
        <div className="flex flex-wrap gap-2">
          {["Contributor", "Developer", "Creator", "Community Builder", "Verified"].map((badge) => (
            <span
              key={badge}
              className="border border-secondary/40 text-secondary rounded-full px-3 py-1 font-mono text-[10px] tracking-wider"
            >
              {badge.toUpperCase()}
            </span>
          ))}
        </div>
      </TerminalCard>
    </div>
  );
}