// Типы для чата

export interface Dialog {
  id: number;
  user_id: number;
  username?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  created_at: string;
  updated_at: string;
  message_count?: number;
  unread_count?: number;
  last_message?: string;
  last_activity?: string;
}

export interface MessageItem {
  id: number;
  dialog_id: number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}
