import clsx from "clsx";

interface ProgressBarProps {
  percent: number;
  accent?: "primary" | "cyan" | "warn" | "danger";
  segments?: { label: string; value: number; color: string }[];
  className?: string;
}

export function ProgressBar({ percent, accent = "primary", segments, className }: ProgressBarProps) {
  const barColors: Record<string, string> = {
    primary: "bg-primary",
    cyan: "bg-secondary",
    warn: "bg-warn",
    danger: "bg-danger",
  };

  return (
    <div className={clsx("w-full", className)}>
      <div className="relative h-2 w-full overflow-hidden rounded-sm bg-panel2 border border-borderline">
        {segments ? (
          segments
            .filter((s) => s.value > 0)
            .map((s) => (
              <div
                key={s.label}
                className="absolute top-0 h-full"
                style={{ left: `${(s.value / 100) * 100}%`, width: `${s.value}%`, background: s.color }}
              />
            ))
        ) : (
          <div
            className={clsx("h-full transition-all duration-500", barColors[accent])}
            style={{ width: `${Math.min(100, percent)}%` }}
          />
        )}
      </div>
      <div className="mt-1 flex justify-between font-mono text-[10px] text-muted">
        {segments ? (
          segments.map((s) => (
            <span key={s.label} style={{ color: s.color }}>
              {s.label} {s.value.toFixed(0)}%
            </span>
          ))
        ) : (
          <>
            <span>{percent.toFixed(0)}%</span>
            <span>▮▮▮▮▮</span>
          </>
        )}
      </div>
    </div>
  );
}