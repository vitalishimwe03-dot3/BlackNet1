import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "../stores/auth";
import { useUIStore } from "../stores/ui";
import { connectNotifications, type WSHandle } from "../services/websocket";

/** Live notification stream. On realtime events, invalidate the notifications query. */
export function useNotificationsSocket() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const pushLog = useUIStore((s) => s.pushLog);

  useEffect(() => {
    if (!user) return;

    let handle: WSHandle | null = null;
    const timeout = setTimeout(() => {
      handle = connectNotifications(() => {
        queryClient.invalidateQueries({ queryKey: ["notifications"] });
        pushLog("[SYSTEM] NOTIFICATION RECEIVED");
      });
    }, 300);

    return () => {
      clearTimeout(timeout);
      handle?.close();
    };
  }, [user, queryClient, pushLog]);
}