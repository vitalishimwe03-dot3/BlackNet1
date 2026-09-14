import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { search } from "../services/endpoints";
import { PageHeader, EmptyState } from "../components/PageLoader";
import { TerminalCard } from "../components/TerminalCard";
import { Avatar } from "../components/Avatar";
import { timeAgo, formatBytes } from "../utils/format";

export function SearchPage() {
  const [query, setQuery] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["search", query],
    queryFn: () => search.global(query).then((r) => r.data),
    enabled: query.trim().length > 0,
  });

  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader title="GLOBAL SEARCH" subtitle="SEARCH: PEOPLE // POSTS // COMMUNITIES // FILES" />

      <div className="mb-6">
        <label className="sr-only" htmlFor="search-input">Search</label>
        <input
          id="search-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="> SEARCH: quantum computing"
          className="w-full bg-panel2 border border-borderline rounded px-4 py-3 font-mono text-sm text-primary placeholder:text-muted/50 focus:border-primary outline-none"
          autoFocus
        />
      </div>

      {query.trim() && isLoading && <div className="font-mono text-xs text-muted blink">INDEXING...</div>}

      {data && (
        <div className="space-y-6">
          {/* Users */}
          {data.users.length > 0 && (
            <SearchSection title="PEOPLE" count={data.users.length}>
              {data.users.map((u) => (
                <Link key={u.id} to={`/profile/${u.username}`} className="flex items-center gap-3 p-2 hover:bg-panel2 rounded">
                  <Avatar username={u.username} avatar={u.avatar} online={u.is_online} size="sm" />
                  <div className="font-mono text-xs">
                    <span className="text-primary">@{u.username}</span>{" "}
                    <span className="text-muted">{timeAgo(u.last_active)}</span>
                  </div>
                </Link>
              ))}
            </SearchSection>
          )}

          {/* Posts */}
          {data.posts.length > 0 && (
            <SearchSection title="POSTS" count={data.posts.length}>
              {data.posts.map((p) => (
                <Link key={p.id} to="/feed" className="block p-2 hover:bg-panel2 rounded">
                  <div className="font-mono text-xs text-primary">[{p.author.username.toUpperCase()}]</div>
                  <div className="font-mono text-xs text-muted truncate">{p.content}</div>
                </Link>
              ))}
            </SearchSection>
          )}

          {/* Communities */}
          {data.communities.length > 0 && (
            <SearchSection title="COMMUNITIES" count={data.communities.length}>
              {data.communities.map((c) => (
                <Link key={c.id} to={`/communities/${c.id}`} className="block p-2 hover:bg-panel2 rounded">
                  <div className="font-mono text-xs text-secondary">/{c.name.toUpperCase()}</div>
                  <div className="font-mono text-[10px] text-muted">{c.member_count} members</div>
                </Link>
              ))}
            </SearchSection>
          )}

          {/* Files */}
          {data.files.length > 0 && (
            <SearchSection title="FILES" count={data.files.length}>
              {data.files.map((f) => (
                <div key={f.id} className="flex items-center justify-between p-2 hover:bg-panel2 rounded">
                  <span className="font-mono text-xs text-muted">{f.original_name}</span>
                  <span className="font-mono text-[10px] text-muted">{formatBytes(f.size_bytes)}</span>
                </div>
              ))}
            </SearchSection>
          )}

          {data.total === 0 && <EmptyState icon="◎" title="NO RESULTS" hint="TRY A DIFFERENT QUERY" />}
        </div>
      )}
    </div>
  );
}

function SearchSection({ title, count, children }: { title: string; count: number; children: React.ReactNode }) {
  return (
    <TerminalCard title={`${title} // ${count}`}>
      <div className="divide-y divide-borderline">{children}</div>
    </TerminalCard>
  );
}