import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { communities } from "../services/endpoints";
import { PageHeader, EmptyState } from "../components/PageLoader";
import { TerminalCard } from "../components/TerminalCard";
import { NeonButton } from "../components/NeonButton";
import { Avatar } from "../components/Avatar";

const SUGGESTED = ["development", "linux", "cybersecurity", "ai", "design", "gaming", "science"];

export function CommunitiesPage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");

  const { data } = useQuery({
    queryKey: ["communities"],
    queryFn: () => communities.list({ page_size: 50 }).then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: () => communities.create({ name, slug: slug || name.toLowerCase().replace(/\s+/g, "-"), description }),
    onSuccess: () => {
      setName("");
      setSlug("");
      setDescription("");
      queryClient.invalidateQueries({ queryKey: ["communities"] });
    },
  });

  const list = data?.results ?? [];

  return (
    <div className="max-w-5xl mx-auto">
      <PageHeader title="NEXUS://COMMUNITIES" subtitle="DISCOVER CHANNELS, CONNECT WITH OTHERS" />

      {/* Discover suggested channels */}
      <TerminalCard title="SUGGESTED CHANNELS" accent="cyan" className="mb-6">
        <div className="flex flex-wrap gap-2">
          {SUGGESTED.map((s) => (
            <button
              key={s}
              onClick={() => {
                setName(s.charAt(0).toUpperCase() + s.slice(1));
                setSlug(s);
                setDescription(`A community for ${s} enthusiasts.`);
                createMutation.mutate();
              }}
              className="border border-borderline rounded px-3 py-1.5 font-mono text-xs text-muted hover:text-secondary hover:border-secondary/40"
            >
              /{s}
            </button>
          ))}
        </div>
      </TerminalCard>

      {/* Create community */}
      <TerminalCard title="CREATE COMMUNITY" accent="primary" className="mb-6">
        <div className="flex flex-wrap gap-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="NAME"
            className="w-40 bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-xs text-primary placeholder:text-muted/50 focus:border-primary outline-none"
          />
          <input
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder="SLUG (e.g. linux)"
            className="w-40 bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-xs text-primary placeholder:text-muted/50 focus:border-primary outline-none"
          />
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="DESCRIPTION"
            className="flex-1 min-w-40 bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-xs text-primary placeholder:text-muted/50 focus:border-primary outline-none"
          />
          <NeonButton size="sm" onClick={() => createMutation.mutate()} disabled={!name.trim()}>
            CREATE
          </NeonButton>
        </div>
      </TerminalCard>

      {list.length === 0 ? (
        <EmptyState icon="◫" title="NO COMMUNITIES" hint="CREATE OR JOIN ONE ABOVE" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {list.map((c) => (
            <div key={c.id} className="terminal-card rounded-lg p-4 hover:border-primary/40 transition-colors">
              <Link to={`/communities/${c.id}`} className="block">
                <div className="flex items-center gap-3">
                  <Avatar username={c.name} avatar={c.icon} size="md" />
                  <div className="flex-1 min-w-0">
                    <div className="font-mono text-sm text-primary truncate">/{c.name.toUpperCase()}</div>
                    <div className="font-mono text-[10px] text-muted">
                      {c.member_count} MEMBERS · {c.visibility.toUpperCase()}
                    </div>
                  </div>
                </div>
                <p className="mt-2 font-mono text-xs text-muted line-clamp-2">{c.description}</p>
                <div className="mt-3 flex justify-between items-center">
                  <span className="font-mono text-[10px] text-secondary">{c.role ? `ROLE: ${c.role.toUpperCase()}` : "OPEN"}</span>
                  <span className="font-mono text-[10px] text-muted">{c.joined_by_me ? "▪ MEMBER" : "· NOT A MEMBER"}</span>
                </div>
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}