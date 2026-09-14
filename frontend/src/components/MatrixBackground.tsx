import { useEffect, useRef } from "react";

/** Subtle matrix-style particle layer behind the app. */
export function MatrixBackground({ density = 30 }: { density?: number }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const chars = "01<>/\\|=+*#0123456789ABCDEF";
    const spans = Array.from({ length: density }, (_, i) => {
      const span = document.createElement("span");
      const size = 10 + Math.random() * 8;
      span.textContent = chars.split("")[Math.floor(Math.random() * chars.length)];
      span.style.left = `${Math.random() * 100}%`;
      span.style.fontSize = `${size}px`;
      span.style.animationDuration = `${6 + Math.random() * 9}s`;
      span.style.animationDelay = `${Math.random() * 6}s`;
      el.appendChild(span);
      if (i === density - 1) return span;
      return span;
    });
    return () => spans.forEach((s) => s.remove());
  }, [density]);

  return <div className="matrix-bg" ref={ref} aria-hidden="true" />;
}