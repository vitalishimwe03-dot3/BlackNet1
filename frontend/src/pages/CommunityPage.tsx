import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { communities } from "../services/endpoints";
import { PageHeader, EmptyState } from "../components/PageLoader";
import { TerminalCard } from "../components/TerminalCard";
import { NeonButton } from "../components/NeonButton";
import { PostCard } from "../components/PostCard";

export function CommunityPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const { data: community } = useQuery({
    queryKey: ["communities", id],
    queryFn: () => communities.detail(id!).then((r) => r.data),
  });

  const { data: postsData } = useQuery({
    queryKey: ["communities", id, "posts"],
    queryFn: () => communities.posts(id!).then((r) => r.data),
  });

  const joinMutation = useMutation({
    mutationFn: () => communities.join(id!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["communities"] }),
  });

  if (!community) {
    return <EmptyState icon="◫" title="LOADING COMMUNITY..." />;
  }

  const postsList = postsData ?? [];

  return (
    <div className="max-w-3xl mx-auto">
      <PageHeader
        title={`NEXUS://COMMUNITIES/ ${community.name.toUpperCase()}`}
        subtitle={`${community.member_count} MEMBERS · ${community.visibility.toUpperCase()} · OWNED BY @${community.owner.username.toUpperCase()}`}
        action={
          !community.joined_by_me ? (
            <NeonButton size="sm" onClick={() => joinMutation.mutate()} disabled={joinMutation.isPending}>
              JOIN COMMUNITY
            </NeonButton>
          ) : null
        }
      />

      <TerminalCard title="DESCRIPTION" accent="cyan" className="mb-6">
        <p className="font-mono text-sm text-gray-300">{community.description || "NO DESCRIPTION"}</p>
      </TerminalCard>

      <div className="font-mono text-xs text-muted mb-4 tracking-widest">// CHANNEL POSTS</div>
      {postsList.length === 0 ? (
        <EmptyState icon="▤" title="NO POSTS IN THIS CHANNEL" />
      ) : (
        postsList.map((post) => <PostCard key={post.id} post={post} />)
      )}
    </div>
  );
}