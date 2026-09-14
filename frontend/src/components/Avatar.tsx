import clsx from "clsx";
import { initials } from "../utils/format";

export function Avatar({ username, avatar, size = "md", online, className }: {
  username: string;
  avatar?: string | null;
  size?: "sm" | "md" | "lg" | "xl";
  online?: boolean;
  className?: string;
}) {
  const sizes = { sm: "h-6 w-6 text-[10px]", md: "h-9 w-9 text-sm", lg: "h-14 w-14 text-lg", xl: "h-24 w-24 text-3xl" };
  return (
    <div className={clsx("relative inline-flex shrink-0", className)}>
      {avatar ? (
        <img src={avatar} alt={username} className={clsx(sizes[size], "rounded-full object-cover border border-borderline")} />
      ) : (
        <div className={clsx(sizes[size], "rounded-full bg-panel2 border border-borderline flex items-center justify-center font-mono text-secondary glow-text-cyan")}>
          {initials(username)}
        </div>
      )}
      {online !== undefined && (
        <span
          className={clsx(
            "absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-bg",
            online ? "bg-primary" : "bg-muted"
          )}
        />
      )}
    </div>
  );
}