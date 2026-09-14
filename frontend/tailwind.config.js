/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#050608",
        panel: "#0B0F12",
        panel2: "#10151A",
        primary: "#00FF88",
        secondary: "#00D9FF",
        warn: "#FFB000",
        danger: "#FF3355",
        muted: "#718096",
        borderline: "#1B252F",
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
        sans: ['"Inter"', "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
      },
      boxShadow: {
        neon: "0 0 12px rgba(0,255,136,0.35), 0 0 2px rgba(0,255,136,0.8)",
        "neon-cyan": "0 0 12px rgba(0,217,255,0.35), 0 0 2px rgba(0,217,255,0.8)",
        panel: "0 4px 24px rgba(0,0,0,0.6)",
      },
      keyframes: {
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.25" },
        },
        flicker: {
          "0%, 100%": { opacity: "1" },
          "90%": { opacity: "1" },
          "92%": { opacity: "0.6" },
          "94%": { opacity: "1" },
          "96%": { opacity: "0.8" },
        },
        rise: {
          "0%": { transform: "translateY(8px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 6px rgba(0,255,136,0.4)" },
          "50%": { boxShadow: "0 0 18px rgba(0,255,136,0.8)" },
        },
      },
      animation: {
        scanline: "scanline 8s linear infinite",
        blink: "blink 1.6s ease-in-out infinite",
        flicker: "flicker 6s linear infinite",
        rise: "rise 0.3s ease-out both",
        pulseGlow: "pulseGlow 2.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};