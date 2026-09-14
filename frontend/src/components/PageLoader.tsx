export function PageLoader({ label = "LOADING..." }: { label?: string }) {
  return (
    <div className="fixed inset-0 z-40 flex flex-col items-center justify-center bg-bg gap-3">
      <span className="font-mono text-primary text-sm blink">{label}</span>
      <div className="h-0.5 w-40 overflow-hidden bg-panel2 rounded">
        <div className="h-full w-1/3 bg-primary animate-[scanline_1s_linear_infinite]" />
      </div>
    </div>
  );
}

export function EmptyState({ icon = "◫", title, hint }: { icon?: string; title: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <span className="text-4xl text-muted mb-3">{icon}</span>
      <div className="font-mono text-sm text-muted">{title}</div>
      {hint && <div className="font-mono text-xs text-muted/60 mt-1">{hint}</div>}
    </div>
  );
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <header className="mb-6 flex items-start justify-between gap-4">
      <div>
        <h1 className="font-mono text-lg md:text-xl text-primary tracking-wide glow-text">{title}</h1>
        {subtitle && <p className="font-mono text-xs text-muted mt-1">{subtitle}</p>}
      </div>
      {action}
    </header>
  );
}