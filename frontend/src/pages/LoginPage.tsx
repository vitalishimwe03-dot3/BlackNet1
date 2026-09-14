import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../stores/auth";
import { NeonButton } from "../components/NeonButton";
import { apiError } from "../services/api";

export function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const login = useAuthStore((s) => s.login);
  const loading = useAuthStore((s) => s.loading);
  const navigate = useNavigate();

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/dashboard");
    } catch (err) {
      setError(await apiError(err));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-bg relative">
      <div className="crt-scan" aria-hidden="true" />
      <div className="w-full max-w-sm terminal-card rounded-lg p-6 relative z-10">
        <div className="mb-6 text-center">
          <div className="font-mono text-2xl text-primary glow-text">◈ BLACKNET</div>
          <div className="font-mono text-xs text-muted mt-1">AUTHENTICATION GATEWAY</div>
        </div>

        {error && (
          <div className="mb-4 border border-danger/40 bg-danger/10 rounded p-2 font-mono text-xs text-danger">
            {error}
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-4">
          <label className="block">
            <span className="font-mono text-xs text-muted">USERNAME</span>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 w-full bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-sm text-primary placeholder:text-muted/60 focus:border-primary outline-none"
              placeholder="username"
              autoComplete="username"
              required
            />
          </label>
          <label className="block">
            <span className="font-mono text-xs text-muted">PASSWORD</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full bg-panel2 border border-borderline rounded px-3 py-2 font-mono text-sm text-primary placeholder:text-muted/60 focus:border-primary outline-none"
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
          </label>

          <NeonButton type="submit" className="w-full" disabled={loading}>
            {loading ? "AUTHENTICATING..." : "ACCESS SYSTEM"}
          </NeonButton>
        </form>

        <p className="mt-4 text-center font-mono text-xs text-muted">
          NO ACCOUNT? <Link to="/register" className="text-secondary hover:underline">SIGN UP</Link>
        </p>
        <p className="mt-2 text-center">
          <Link to="/" className="font-mono text-[10px] text-muted/60 hover:text-muted">
            ← BACK TO NEXUS
          </Link>
        </p>
      </div>
    </div>
  );
}