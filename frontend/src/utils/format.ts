export function formatBytes(bytes: number): string {
  if (!bytes || bytes <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / Math.pow(1024, i);
  return `${value.toFixed(value >= 100 || i === 0 ? 0 : 2)} ${units[i]}`;
}

export function formatStorage(bytes: number): string {
  const gb = bytes / 1024 ** 3;
  return `${gb.toFixed(2)} GB`;
}

export function formatPercent(bytes: number, total: number): string {
  if (!total) return "0%";
  return `${Math.min(100, Math.round((bytes / total) * 100))}%`;
}

export function timeAgo(date: string): string {
  const then = new Date(date).getTime();
  const diff = Date.now() - then;
  const s = Math.floor(diff / 1000);
  if (s < 10) return "JUST NOW";
  if (s < 60) return `${s} SECONDS AGO`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} MINUTE${m > 1 ? "S" : ""} AGO`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} HOUR${h > 1 ? "S" : ""} AGO`;
  const d = Math.floor(h / 24);
  if (d < 30) return `${d} DAY${d > 1 ? "S" : ""} AGO`;
  return new Date(date).toLocaleDateString();
}

export function clockTime(date: string): string {
  return new Date(date).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function shortId(id: string): string {
  return id.slice(0, 8).toUpperCase();
}

export function initials(username: string): string {
  return username.slice(0, 2).toUpperCase();
}