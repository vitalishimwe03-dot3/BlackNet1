import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { Post } from "../types";
import { posts } from "../services/endpoints";
import { Avatar } from "./Avatar";
import { NeonButton } from "./NeonButton";
import { timeAgo } from "../utils/format";

export function PostCard({ post }: { post: Post }) {
  const queryClient = useQueryClient();
  const [comment, setComment] = useState("");

  const likeMutation = useMutation({
    mutationFn: () => posts.like(post.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["posts"] }),
  });

  const commentMutation = useMutation({
    mutationFn: () => posts.comment(post.id, comment),
    onSuccess: () => {
      setComment("");
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
  });

  return (
    <article className="terminal-card rounded-lg p-4 mb-4">
      <header className="flex items-center gap-3">
        <Avatar username={post.author.username} avatar={post.author.avatar} size="sm" online={post.author.is_online} />
        <div className="flex-1">
          <div className="font-mono text-sm text-primary">
            [{post.author.username.toUpperCase()}]{post.author.username.length < 8 ? "".padEnd(8 - post.author.username.length, "_") : ""} <span className="text-muted">//</span> TRANSMISSION
          </div>
          <div className="font-mono text-[10px] text-muted">{timeAgo(post.created_at)}</div>
        </div>
        <span className="font-mono text-[10px] text-muted border border-borderline rounded px-1.5 py-0.5 uppercase">{post.post_type}</span>
      </header>

      <p className="mt-3 whitespace-pre-wrap font-mono text-sm text-gray-300">{post.content}</p>

      {post.image && (
        <img src={post.image} alt="" loading="lazy" className="mt-3 rounded border border-borderline max-h-80 object-contain w-full" />
      )}
      {post.video && (
        <video controls preload="metadata" className="mt-3 rounded border border-borderline max-h-80 w-full">
          <source src={post.video} />
        </video>
      )}
      {post.link_url && (
        <a href={post.link_url} target="_blank" rel="noreferrer" className="mt-3 block font-mono text-xs text-secondary underline break-all">
          LINK: {post.link_url}
        </a>
      )}

      <footer className="mt-4 flex items-center gap-4 font-mono text-xs text-muted">
        <button
          onClick={() => likeMutation.mutate()}
          className={post.liked_by_me ? "text-danger" : "hover:text-danger"}
        >
          ▲ {post.like_count}
        </button>
        <span>◉ {post.comment_count} COMMENTS</span>
        <span>◔ {post.view_count} VIEWS</span>
        <span className="ml-auto text-[10px]">{post.is_edited ? "[EDITED]" : ""}</span>
      </footer>

      <div className="mt-3 flex gap-2">
        <input
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && commentMutation.mutate()}
          placeholder="ADD COMMENT..."
          className="flex-1 bg-panel2 border border-borderline rounded px-3 py-1.5 font-mono text-xs text-primary placeholder:text-muted/50 focus:border-primary outline-none"
        />
        <NeonButton size="sm" variant="ghost" onClick={() => commentMutation.mutate()}>
          SEND
        </NeonButton>
      </div>
    </article>
  );
}