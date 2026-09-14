import { create } from "zustand";
import { api, apiError, tokenStore, type Tokens } from "../services/api";
import type { Me } from "../types";

interface AuthState {
  user: Me | null;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loadMe: () => Promise<void>;
  updateUser: (patch: Partial<Me>) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,
  error: null,

  login: async (username, password) => {
    set({ loading: true, error: null });
    try {
      const { data } = await api.post<{ access: string; refresh: string; user: Me }>("/auth/login", {
        username,
        password,
      });
      const tokens: Tokens = { access: data.access, refresh: data.refresh };
      tokenStore.set(tokens);
      set({ user: data.user });
    } catch (err) {
      set({ error: await apiError(err) });
      throw err;
    } finally {
      set({ loading: false });
    }
  },

  register: async (username, email, password) => {
    set({ loading: true, error: null });
    try {
      const { data } = await api.post<{ access: string; refresh: string; user: Me }>("/auth/register", {
        username,
        email,
        password,
      });
      tokenStore.set({ access: data.access, refresh: data.refresh });
      set({ user: data.user });
    } catch (err) {
      set({ error: await apiError(err) });
      throw err;
    } finally {
      set({ loading: false });
    }
  },

  logout: async () => {
    const tokens = tokenStore.get();
    try {
      if (tokens?.refresh) {
        await api.post("/auth/logout", { refresh: tokens.refresh });
      }
    } catch {
      /* token may already be invalid */
    }
    tokenStore.clear();
    set({ user: null });
  },

  loadMe: async () => {
    if (!tokenStore.get()) return;
    set({ loading: true });
    try {
      const { data } = await api.get<Me>("/users/me");
      set({ user: data });
    } catch {
      /* 401 handled by interceptor */
    } finally {
      set({ loading: false });
    }
  },

  updateUser: async (patch) => {
    await api.patch("/users/me/profile", patch);
    const { data } = await api.get<Me>("/users/me");
    set({ user: data });
  },
}));