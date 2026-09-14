import { api } from "./api";
import type {
  Comment,
  Community,
  Conversation,
  FileEntry,
  Folder,
  Me,
  Message,
  Notification,
  Paginated,
  Post,
  SecurityOverview,
  ShareLinkResult,
  StorageUsage,
  User,
} from "../types";

// ---- Auth/profile ----
export const auth = {
  me: () => api.get<Me>("/users/me"),
  updateMe: (patch: Partial<Me>) => api.patch<Me>("/users/me", patch),
  profile: (username: string) => api.get<User>(`/users/${username}`),
  sessions: () => api.get<Paginated<unknown>>("/users/me/sessions"),
};

// ---- Posts ----
export const posts = {
  list: (params?: Record<string, unknown>) => api.get<Paginated<Post>>("/posts", { params }),
  feed: (params?: Record<string, unknown>) => api.get<Paginated<Post>>("/posts/feed", { params }),
  create: (body: FormData) => api.post<Post>("/posts", body),
  like: (id: string) => api.post<{ liked: boolean; like_count: number }>(`/posts/${id}/like`),
  comment: (id: string, content: string) => api.post<Comment>(`/posts/${id}/comments`, { content }),
  comments: (id: string) => api.get<Paginated<Comment>>(`/posts/${id}/comments`),
  vote: (id: string, choice: number) => api.post(`/posts/${id}/vote`, { choice }),
};

// ---- Messages ----
export const messages = {
  list: () => api.get<Paginated<Conversation>>("/messages"),
  direct: (username: string) => api.post<Conversation>("/messages/direct", { username }),
  group: (name: string, members: string[]) => api.post<Conversation>("/messages/ensure_group", { name, members }),
  history: (id: string, params?: Record<string, unknown>) => api.get<Paginated<Message>>(`/messages/${id}/history`, { params }),
  send: (id: string, content: string) => api.post<Message>(`/messages/${id}/send`, { content }),
};

// ---- Files ----
export const files = {
  list: (params?: Record<string, unknown>) => api.get<Paginated<FileEntry>>("/files", { params }),
  folders: (params?: Record<string, unknown>) => api.get<Paginated<Folder>>("/files/folders", { params }),
  createFolder: (name: string, parent?: string | null) =>
    api.post<Folder>("/files/folders", { name, parent }),
  usage: () => api.get<StorageUsage>("/files/usage"),
  upload: (form: FormData) =>
    api.post<FileEntry>("/files/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  rename: (id: string, name: string) => api.post<FileEntry>(`/files/${id}/rename`, { name }),
  move: (id: string, folder: string | null) => api.post<FileEntry>(`/files/${id}/move`, { folder }),
  remove: (id: string) => api.delete(`/files/${id}`),
  share: (id: string, opts?: { expires_hours?: number; max_downloads?: number; password?: string }) =>
    api.post<ShareLinkResult>(`/files/${id}/share`, opts || {}),
};

// ---- Communities ----
export const communities = {
  list: (params?: Record<string, unknown>) => api.get<Paginated<Community>>("/communities", { params }),
  detail: (id: string) => api.get<Community>(`/communities/${id}`),
  create: (body: Record<string, unknown>) => api.post<Community>("/communities", body),
  join: (id: string) => api.post<{ joined: boolean }>(`/communities/${id}/join`),
  leave: (id: string) => api.post<{ detail: string }>(`/communities/${id}/leave`),
  posts: (id: string) => api.get<Post[]>(`/communities/${id}/posts`),
};

// ---- Notifications ----
export const notifications = {
  list: (params?: Record<string, unknown>) => api.get<Paginated<Notification>>("/notifications", { params }),
  markRead: (id: string) => api.patch<Notification>(`/notifications/${id}`, { is_read: true }),
  readAll: () => api.post("/notifications/read-all"),
};

// ---- Search ----
export const search = {
  global: (q: string) =>
    api.get<{
      query: string;
      users: User[];
      posts: Post[];
      communities: Community[];
      files: FileEntry[];
      total: number;
    }>("/search", { params: { q } }),
};

// ---- Security ----
export const security = {
  overview: () => api.get<SecurityOverview>("/security/overview"),
  events: () => api.get<Paginated<unknown>>("/security/events"),
};

export const storageBytes = (me: Me) => me.storage_bytes_used;