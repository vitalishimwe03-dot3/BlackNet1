import type { ReactNode } from "react";
import clsx from "clsx";

interface TerminalCardProps {
  title?: string;
  icon?: ReactNode;
  accent?: "primary" | "cyan" | "warn" | "danger";
  className?: string;
  action?: ReactNode;
  children: ReactNode;
}

const accents = {
  primary: "border-primary/30",
  cyan: "border-secondary/30",
  warn: "border-warn/30",
  danger: "border-danger/30",
};

export function TerminalCard({ title, icon, accent = "primary", className, action, children }: TerminalCardProps) {
  return (
    <section className={clsx("terminal-card rounded-lg overflow-hidden", className)}>
      {(title || action) && (
        <header className="flex items-center justify-between px-4 py-2 border-b border-borderline bg-panel2/60">
          <h2 className="flex items-center gap-2 font-mono text-sm tracking-wider text-muted">
            {icon}
            {title && <span>{title}</span>}
          </h2>
          {action}
        </header>
      )}
      <div className={clsx(accents[accent], "p-4")}>{children}</div>
    </section>
  );
}