import { useState, type FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { useAuthStore } from "../stores/auth";
import { PageHeader } from "../components/PageLoader";
import { TerminalCard } from "../components/TerminalCard";
import { NeonButton } from "../components/NeonButton";
import type { Me } from "../types";

export function SettingsPage() {
  const me = useAuthStore((s) => s.user)!;
  const updateUser = useAuthStore((s) => s.updateUser);
  const queryClient = useQueryClient();
  const [saved, setSaved] = useState("");

  const [bio, setBio] = useState(me.bio ?? "");
  const [visibility, setVisibility] = useState(me.profile_visibility);
  const [reputationPublic, setReputationPublic] = useState(me.reputation_public);
  const [notifyMessages, setNotifyMessages] = useState(me.notify_new_messages);
  const [notifyLikes, setNotifyLikes] = useState(me.notify_likes);
  const [notifyComments, setNotifyComments] = useState(me.notify_comments);
  const [notifyFollowers, setNotifyFollowers] = useState(me.notify_followers);
  const [notifyMentions, setNotifyMentions] = useState(me.notify_mentions);
  const [notifySecurity, setNotifySecurity] = useState(me.notify_security);
  const [emailNotif, setEmailNotif] = useState(me.email_notifications);

  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const profileMutation = useMutation({
    mutationFn: () =>
      updateUser({
        bio,
        profile_visibility: visibility,
        reputation_public: reputationPublic,
        notify_new_messages: notifyMessages,
        notify_likes: notifyLikes,
        notify_comments: notifyComments,
        notify_followers: notifyFollowers,
        notify_mentions: notifyMentions,
        notify_security: notifySecurity,
        email_notifications: emailNotif,
      } as Partial<Me>),
    onSuccess: () => {
      setSaved("SETTINGS STORED");
      queryClient.invalidateQueries({ queryKey: ["users", "me"] });
    },
  });

  const passwordMutation = useMutation({
    mutationFn: () => api.post("/auth/change-password", { old_password: oldPassword, new_password: newPassword }),
    onSuccess: () => {
      setSaved("PASSWORD UPDATED");
      setOldPassword("");
      setNewPassword("");
    },
    onError: () => setSaved("PASSWORD CHANGE FAILED"),
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    profileMutation.mutate();
  };

  return (
    <div className="max-w-3xl mx-auto">
      <PageHeader title="SETTINGS" subtitle="ACCOUNT // PRIVACY // NOTIFICATIONS" />

      {saved && <div className="mb-4 border border-primary/40 bg-primary/5 rounded p-2 font-mono text-xs text-primary">{saved}</div>}

      <form onSubmit={onSubmit} className="space-y-4">
        <TerminalCard title="PROFILE" accent="primary">
          <div className="space-y-3">
            <label className="block">
              <span className="font-mono text-xs text-muted">BIO</span>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={3}
                maxLength={500}
                className="mt-1 w-full bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-sm text-primary placeholder:text-muted/50 focus:border-primary outline-none resize-none"
              />
            </label>
            <label className="block">
              <span className="font-mono text-xs text-muted">PROFILE VISIBILITY</span>
              <select
                value={visibility}
                onChange={(e) => setVisibility(e.target.value as Me["profile_visibility"])}
                className="mt-1 w-full bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-sm text-primary outline-none focus:border-primary"
              >
                <option value="public">PUBLIC</option>
                <option value="private">PRIVATE</option>
                <option value="followers">FOLLOWERS ONLY</option>
              </select>
            </label>
            <label className="flex items-center gap-2 font-mono text-xs text-muted">
              <input
                type="checkbox"
                checked={reputationPublic}
                onChange={(e) => setReputationPublic(e.target.checked)}
                className="accent-[#00FF88]"
              />
              SHOW REPUTATION ON PROFILE
            </label>
          </div>
        </TerminalCard>

        <TerminalCard title="NOTIFICATIONS" accent="cyan">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <Toggle label="NEW MESSAGES" checked={notifyMessages} onChange={setNotifyMessages} />
            <Toggle label="LIKES" checked={notifyLikes} onChange={setNotifyLikes} />
            <Toggle label="COMMENTS" checked={notifyComments} onChange={setNotifyComments} />
            <Toggle label="NEW FOLLOWERS" checked={notifyFollowers} onChange={setNotifyFollowers} />
            <Toggle label="MENTIONS" checked={notifyMentions} onChange={setNotifyMentions} />
            <Toggle label="SECURITY ALERTS" checked={notifySecurity} onChange={setNotifySecurity} />
            <Toggle label="EMAIL NOTIFICATIONS" checked={emailNotif} onChange={setEmailNotif} />
          </div>
        </TerminalCard>

        <div className="flex justify-end">
          <NeonButton type="submit" disabled={profileMutation.isPending}>
            {profileMutation.isPending ? "STORING..." : "SAVE SETTINGS"}
          </NeonButton>
        </div>
      </form>

      <TerminalCard title="CHANGE PASSWORD" accent="danger" className="mt-6">
        <div className="space-y-3">
          <input
            type="password"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            placeholder="CURRENT PASSWORD"
            className="w-full bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-sm text-primary placeholder:text-muted/50 focus:border-danger outline-none"
          />
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="NEW PASSWORD (MIN 10)"
            className="w-full bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-sm text-primary placeholder:text-muted/50 focus:border-danger outline-none"
          />
          <NeonButton variant="danger" size="sm" onClick={() => passwordMutation.mutate()} disabled={!oldPassword || !newPassword}>
            UPDATE PASSWORD
          </NeonButton>
        </div>
      </TerminalCard>
    </div>
  );
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="flex items-center justify-between gap-2 font-mono text-xs text-muted">
      {label}
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`h-5 w-9 rounded-full border relative transition-colors ${checked ? "bg-primary/30 border-primary" : "bg-panel2 border-borderline"}`}
      >
        <span
          className={`absolute top-0.5 h-3.5 w-3.5 rounded-full transition-all ${checked ? "left-[18px] bg-primary" : "left-0.5 bg-muted"}`}
        />
      </button>
    </label>
  );
}