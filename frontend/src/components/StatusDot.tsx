import clsx from "clsx";

export function StatusDot({ online, pulse = true }: { online?: boolean; pulse?: boolean }) {
  return (
    <span
      className={clsx(
        "inline-block h-2 w-2 rounded-full",
        online ? "bg-primary shadow-[0_0_6px_rgba(0,255,136,0.8)]" : "bg-muted",
        pulse && online && "animate-pulseGlow"
      )}
      aria-label={online ? "online" : "offline"}
    />
  );
}

export function SystemIndicator({ label, ok = true }: { label: string; ok?: boolean }) {
  return (
    <div className="flex items-center gap-2 font-mono text-xs text-muted">
      <StatusDot online={ok} pulse={false} />
      <span>{label}</span>
    </div>
  );
}