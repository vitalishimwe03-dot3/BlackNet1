import type { ButtonHTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

interface NeonButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "cyan" | "ghost" | "danger" | "warn";
  size?: "sm" | "md" | "lg";
  children: ReactNode;
}

const variants = {
  primary: "bg-primary/10 border-primary/40 text-primary hover:bg-primary/20 shadow-neon",
  cyan: "bg-secondary/10 border-secondary/40 text-secondary hover:bg-secondary/20 shadow-neon-cyan",
  ghost: "bg-transparent border-borderline text-muted hover:text-primary hover:border-primary/40",
  danger: "bg-danger/10 border-danger/40 text-danger hover:bg-danger/20",
  warn: "bg-warn/10 border-warn/40 text-warn hover:bg-warn/20",
};

const sizes = {
  sm: "px-2 py-1 text-xs",
  md: "px-4 py-2 text-sm",
  lg: "px-6 py-3 text-base",
};

export function NeonButton({ variant = "primary", size = "md", children, className, ...rest }: NeonButtonProps) {
  return (
    <button
      className={clsx(
        "border rounded font-mono tracking-wider transition-colors duration-200 disabled:opacity-40 disabled:cursor-not-allowed",
        variants[variant],
        sizes[size],
        className
      )}
      {...rest}
    >
      {children}
    </button>
  );
}