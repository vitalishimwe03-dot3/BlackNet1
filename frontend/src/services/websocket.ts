// Helpers for the two WebSocket streams (messaging + notifications).

const WS_BASE = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

type Handler = (payload: unknown) => void;

export interface WSHandle {
  send: (event: string, payload: unknown) => void;
  close: () => void;
}

function tokenParam(): string {
  try {
    const raw = localStorage.getItem("blacknet_tokens");
    const tokens = raw ? JSON.parse(raw) : null;
    return tokens?.access ? `?token=${encodeURIComponent(tokens.access)}` : "";
  } catch {
    return "";
  }
}

interface Conn {
  ws: WebSocket | null;
  closed: boolean;
  retryTimer: ReturnType<typeof setTimeout> | null;
}

function createHandle(
  conn: Conn,
  onClose: ((c: Conn) => void) | null
): WSHandle {
  return {
    send: (event, payload) => {
      if (conn.ws && conn.ws.readyState === WebSocket.OPEN) {
        conn.ws.send(JSON.stringify({ event, ...(payload as object) }));
      }
    },
    close: () => {
      conn.closed = true;
      if (conn.retryTimer !== null) {
        clearTimeout(conn.retryTimer);
        conn.retryTimer = null;
      }
      if (conn.ws) {
        try {
          conn.ws.onclose = null;
          conn.ws.close();
        } catch {
          /* already closed */
        }
      }
    },
  };
}

function openWithRetry(
  url: string,
  onMessage: (ev: MessageEvent) => void,
  onEvent?: () => void
): WSHandle {
  const conn: Conn = { ws: null, closed: false, retryTimer: null };

  const connect = () => {
    if (conn.closed) return;
    conn.ws = new WebSocket(url);
    conn.ws.onmessage = onMessage;
    conn.ws.onclose = () => {
      if (!conn.closed) {
        conn.retryTimer = setTimeout(connect, 4000);
      }
    };
    conn.ws.onerror = () => {
      try {
        conn.ws?.close();
      } catch {
        /* ignore */
      }
      if (onEvent) onEvent();
    };
  };

  connect();

  return createHandle(conn, null);
}

export function connectNotifications(onEvent: Handler): WSHandle {
  return openWithRetry(
    `${WS_BASE}/notifications${tokenParam()}`,
    (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.event === "notification") onEvent(msg.payload);
      } catch {
        /* ignore malformed frames */
      }
    }
  );
}

export function connectConversation(conversationId: string, onEvent: Handler): WSHandle {
  const url = `${WS_BASE}/conversations/${conversationId}${tokenParam()}`;
  const conn: Conn = { ws: null, closed: false, retryTimer: null };

  const connect = () => {
    if (conn.closed) return;
    conn.ws = new WebSocket(url);
    conn.ws.onmessage = (ev) => {
      try {
        onEvent(JSON.parse(ev.data));
      } catch {
        /* ignore malformed frames */
      }
    };
    conn.ws.onclose = () => {
      if (!conn.closed) {
        conn.retryTimer = setTimeout(connect, 4000);
      }
    };
  };

  connect();

  return createHandle(conn, null);
}