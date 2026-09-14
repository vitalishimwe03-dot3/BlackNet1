import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { MatrixBackground } from "../components/MatrixBackground";
import { NeonButton } from "../components/NeonButton";
import { useAuthStore } from "../stores/auth";

const BOOT = [
  "INITIALIZING NETWORK...",
  "LOADING USER SPACE...",
  "STORAGE SYSTEM ONLINE",
  "MESSAGING SYSTEM ONLINE",
  "COMMUNITY GRID ONLINE",
  "NEXUS READY",
];

const FEATURES = [
  { icon: "◈", title: "5 GB STORAGE", desc: "Files, images, video and archives inside your own quota." },
  { icon: "✉", title: "REAL-TIME MESSAGING", desc: "Instant DMs and groups over WebSockets." },
  { icon: "▤", title: "SOCIAL FEED", desc: "Transmissions, likes, comments, polls and communities." },
  { icon: "◉", title: "DIGITAL VAULT", desc: "A protected area for your most important files." },
  { icon: "◈", title: "SECURITY CENTER", desc: "Sessions, 2FA, login history and alerts." },
  { icon: "⚙", title: "REPUTATION", desc: "Badges for contributors, builders and creators." },
];

export function LandingPage() {
  const [booted, setBooted] = useState<string[]>([]);
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setBooted((prev) => [...prev, BOOT[i]]);
      i += 1;
      if (i >= BOOT.length) clearInterval(interval);
    }, 450);
    return () => clearInterval(interval);
  }, []);

  const ready = booted.length >= BOOT.length;

  return (
    <div className="relative min-h-screen overflow-hidden bg-bg">
      <MatrixBackground density={24} />
      <div className="crt-scan" aria-hidden="true" />

      {/* Top bar */}
      <header className="relative z-10 flex items-center justify-between px-6 py-4">
        <div className="font-mono text-primary tracking-wide glow-text">
          ◈ BLACKNET <span className="text-muted text-xs">// NEXUS</span>
        </div>
        <div className="flex items-center gap-2">
          {user ? (
            <Link to="/dashboard">
              <NeonButton size="sm">ENTER NEXUS</NeonButton>
            </Link>
          ) : (
            <>
              <Link to="/login">
                <NeonButton variant="ghost" size="sm">
                  LOGIN
                </NeonButton>
              </Link>
              <Link to="/register">
                <NeonButton size="sm">SIGN UP</NeonButton>
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Hero */}
      <main className="relative z-10 flex flex-col items-center text-center px-6 pt-16 md:pt-24 pb-20">
        <div className="font-mono text-xs md:text-sm text-secondary tracking-[0.3em] mb-4 blink">
          {ready ? "NEXUS READY" : "BOOTING..."}
        </div>
        <h1 className="font-mono text-4xl md:text-6xl text-primary glow-text font-bold tracking-wider">
          WELCOME TO THE NEXUS
        </h1>
        <p className="mt-4 max-w-xl text-gray-300 text-base md:text-lg">
          A private digital space for communication, creativity and collaboration.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link to={user ? "/dashboard" : "/register"}>
            <NeonButton size="lg">ENTER NEXUS</NeonButton>
          </Link>
          <Link to="#system">
            <NeonButton variant="cyan" size="lg">
              EXPLORE SYSTEM
            </NeonButton>
          </Link>
        </div>

        {/* Boot terminal */}
        <div className="mt-12 w-full max-w-lg terminal-card rounded-lg text-left p-4 font-mono text-xs leading-6">
          {booted.map((line, i) => (
            <div key={i} className="text-secondary">
              <span className="text-muted">[{String(Date.now() % 10000).padStart(4, "0")}]</span> {line}
              {i === booted.length - 1 && !ready && <span className="blink text-primary">▌</span>}
            </div>
          ))}
          {ready && <div className="text-primary glow-text">ACCESS GRANTED // WAITING FOR OPERATOR...</div>}
        </div>
      </main>

      {/* System features */}
      <section id="system" className="relative z-10 max-w-5xl mx-auto px-6 pb-20">
        <h2 className="font-mono text-sm text-muted tracking-widest mb-6">// SYSTEM MODULES</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((f) => (
            <div key={f.title} className="terminal-card rounded-lg p-5 transition-transform hover:-translate-y-0.5">
              <div className="text-primary text-xl mb-2">{f.icon}</div>
              <div className="font-mono text-sm text-primary tracking-wider">{f.title}</div>
              <p className="mt-2 text-sm text-muted">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="relative z-10 border-t border-borderline py-6 text-center font-mono text-[10px] text-muted">
        BLACKNET // A SAFE PRIVATE NETWORK — NORMAL INTERNET, NORMAL RULES
      </footer>
    </div>
  );
}