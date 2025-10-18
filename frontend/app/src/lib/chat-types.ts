// Типы для чата

export interface LastMessage {
  text: string;
  timestamp: string;
  role: string;
}

export interface Dialog {
  user_id: number;
  username?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  last_message: LastMessage | null;
  unread_count: number;
  total_messages: number;
}

export interface MessageItem {
  id: number;
  text: string;
  role: "user" | "assistant" | "system";
  timestamp: string;
}
