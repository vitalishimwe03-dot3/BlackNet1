// Shared TypeScript domain types mirroring the Django API responses.

export interface User {
  id: string;
  username: string;
  avatar: string | null;
  bio: string;
  created_at: string;
  last_active: string;
  is_online: boolean;
  profile_visibility: "public" | "private" | "followers";
  reputation_public: boolean;
}

export interface Me extends User {
  email: string;
  is_email_verified: boolean;
  is_2fa_enabled: boolean;
  storage_bytes_total: number;
  storage_bytes_used: number;
  notify_new_messages: boolean;
  notify_likes: boolean;
  notify_comments: boolean;
  notify_followers: boolean;
  notify_mentions: boolean;
  notify_community: boolean;
  notify_security: boolean;
  email_notifications: boolean;
}

export interface Post {
  id: string;
  author: User;
  content: string;
  post_type: "text" | "image" | "video" | "link" | "poll" | "file";
  community: string | null;
  image: string | null;
  video: string | null;
  file: string | null;
  link_url: string | null;
  poll_data: PollData | null;
  view_count: number;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
  like_count: number;
  comment_count: number;
  liked_by_me: boolean;
  bookmarked_by_me: boolean;
}

export interface PollData {
  question: string;
  options: string[];
  votes?: Record<number, number>;
}

export interface Comment {
  id: string;
  post: string;
  author: User;
  parent: string | null;
  content: string;
  is_deleted: boolean;
  created_at: string;
  like_count: number;
}

export interface Conversation {
  id: string;
  type: "private" | "group";
  name: string;
  created_at: string;
  last_message_at: string;
  last_message: string;
  members: User[];
  unread_count: number;
  partner?: string | null;
}

export interface Message {
  id: string;
  conversation: string;
  sender: User;
  content: string;
  reply_to: string | null;
  attachment_file?: string | null;
  attachment_image?: string | null;
  attachment_video?: string | null;
  read_by: string[];
  reactions: Record<string, string>;
  is_edited: boolean;
  is_deleted: boolean;
  created_at: string;
  reply_preview?: string | null;
}

export interface FileEntry {
  id: string;
  owner: string;
  folder: string | null;
  original_name: string;
  stored_name: string;
  size_bytes: number;
  content_type: string;
  category: "image" | "video" | "document" | "audio" | "archive" | "other";
  sha256: string;
  is_processed: boolean;
  thumbnail: string | null;
  width: number | null;
  height: number | null;
  duration_seconds: number | null;
  in_vault: boolean;
  last_accessed: string;
  created_at: string;
  url: string | null;
  thumbnail_url: string | null;
  share_url: string | null;
}

export interface Folder {
  id: string;
  parent: string | null;
  name: string;
  created_at: string;
  file_count: number;
}

export interface StorageUsage {
  total_bytes: number;
  used_bytes: number;
  free_bytes: number;
  image_bytes: number;
  video_bytes: number;
  document_bytes: number;
  audio_bytes: number;
  archive_bytes: number;
  other_bytes: number;
  file_count: number;
  updated_at: string;
}

export interface Community {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string | null;
  banner: string | null;
  owner: User;
  visibility: "public" | "private";
  is_active: boolean;
  created_at: string;
  member_count: number;
  joined_by_me: boolean;
  role?: string | null;
}

export interface Notification {
  id: string;
  actor: string | null;
  kind: string;
  message: string;
  post?: string | null;
  message_obj?: string | null;
  file?: string | null;
  data: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
  post_detail?: { post_id: string; content: string } | null;
}

export interface ShareLinkResult {
  token: string;
  url: string;
  expires_at: string | null;
}

export interface Session {
  id: string;
  device_name: string;
  ip_address: string | null;
  user_agent: string;
  is_current: boolean;
  created_at: string;
  last_seen: string;
}

export interface SecurityOverview {
  sessions: Session[];
  login_history: SecurityEvent[];
  password_changes: number;
  two_factor_enabled: boolean;
  suspicious_logins: number;
  device_count: number;
}

export interface SecurityEvent {
  id: string;
  event_type: string;
  ip_address: string | null;
  user_agent: string;
  details: Record<string, unknown>;
  created_at: string;
}

export interface Report {
  id: string;
  reporter: string;
  category: string;
  target_type: string;
  target_id: string;
  reason: string;
  status: string;
  resolution_note: string;
  created_at: string;
  resolved_at: string | null;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}