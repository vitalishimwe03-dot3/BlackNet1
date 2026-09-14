import { create } from "zustand";

interface UIState {
  commandPaletteOpen: boolean;
  sidebarOpen: boolean;
  systemLog: string[];
  pushLog: (entry: string) => void;
  setCommandPalette: (open: boolean) => void;
  setSidebar: (open: boolean) => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>((set, get) => ({
  commandPaletteOpen: false,
  sidebarOpen: true,
  systemLog: [],
  pushLog: (entry) => {
    const log = [...get().systemLog, entry].slice(-50);
    set({ systemLog: log });
  },
  setCommandPalette: (open) => set({ commandPaletteOpen: open }),
  setSidebar: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));