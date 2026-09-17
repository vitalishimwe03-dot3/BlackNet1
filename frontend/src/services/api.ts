import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

export const API_BASE = import.meta.env.VITE_API_URL || "/api";

export interface Tokens {
  access: string;
  refresh: string;
}

const KEY = "blacknet_tokens";

export const tokenStore = {
  get(): Tokens | null {
    try {
      const raw = localStorage.getItem(KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  set(tokens: Tokens) {
    localStorage.setItem(KEY, JSON.stringify(tokens));
  },
  clear() {
    localStorage.removeItem(KEY);
  },
};

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

let refreshPromise: Promise<string> | null = null;

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const tokens = tokenStore.get();
  if (tokens?.access) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const tokens = tokenStore.get();

    if (error.response?.status === 401 && tokens?.refresh && !original?._retry) {
      original._retry = true;
      try {
        const access = await (refreshPromise ?? (refreshPromise = doRefresh(tokens.refresh).finally(() => (refreshPromise = null))));
        tokenStore.set({ ...tokens, access });
        original.headers.Authorization = `Bearer ${access}`;
        return api(original);
      } catch {
        tokenStore.clear();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

async function doRefresh(refresh: string): Promise<string> {
  const { data } = await axios.post<{ access: string }>(`${API_BASE}/auth/refresh`, { refresh });
  return data.access;
}

export async function apiError(error: unknown): Promise<string> {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { detail?: string; code?: string; errors?: Record<string, string[]> } | string | undefined;
    if (typeof data === "string") return data;
    if (data) {
      if (data.detail) return data.detail;
      if (data.errors) {
        const msgs = Object.entries(data.errors)
          .flatMap(([, v]) => (Array.isArray(v) ? v : [String(v)]))
          .join("; ");
        if (msgs) return msgs;
      }
      if (data.code) return data.code;
      const fieldErrors = Object.entries(data).filter(([k]) => k !== "detail" && k !== "code");
      if (fieldErrors.length > 0) {
        const first = fieldErrors[0];
        const msgs = Array.isArray(first[1]) ? (first[1] as string[]).join("; ") : String(first[1]);
        return `${first[0].toUpperCase()}: ${msgs}`;
      }
    }
    if (error.response?.status) {
      return `REQUEST FAILED // STATUS ${error.response.status}`;
    }
    return error.message;
  }
  return String(error);
}