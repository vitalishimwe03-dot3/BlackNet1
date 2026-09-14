import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { posts } from "../services/endpoints";
import { PostCard } from "../components/PostCard";
import { PageHeader, EmptyState } from "../components/PageLoader";
import { NeonButton } from "../components/NeonButton";

export function FeedPage() {
  const [draft, setDraft] = useState("");
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: () => {
      const form = new FormData();
      form.append("content", draft);
      form.append("post_type", "text");
      return posts.create(form);
    },
    onSuccess: () => {
      setDraft("");
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
  });

  const feed = useQuery({
    queryKey: ["posts", "feed"],
    queryFn: () => posts.feed({ page_size: 25 }).then((r) => r.data),
  });

  const all = feed.data?.results ?? [];

  return (
    <div className="max-w-3xl mx-auto">
      <PageHeader title="TRANSMISSION FEED" subtitle="NEXUS://FEED — WHAT'S NEW ACROSS THE NETWORK" />

      {/* Compose */}
      <div className="terminal-card rounded-lg p-4 mb-6">
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="> COMPOSE TRANSMISSION..."
          rows={3}
          className="w-full bg-panel2 border border-borderline rounded p-3 font-mono text-sm text-primary placeholder:text-muted/50 focus:border-primary outline-none resize-none"
          maxLength={10000}
        />
        <div className="mt-2 flex justify-end">
          <NeonButton size="sm" onClick={() => createMutation.mutate()} disabled={!draft.trim() || createMutation.isPending}>
            {createMutation.isPending ? "TRANSMITTING..." : "TRANSMIT"}
          </NeonButton>
        </div>
      </div>

      {all.length === 0 ? (
        <EmptyState icon="▤" title="NO TRANSMISSIONS" hint="POSTS FROM PEOPLE YOU FOLLOW APPEAR HERE" />
      ) : (
        all.map((post) => <PostCard key={post.id} post={post} />)
      )}
    </div>
  );
}