// Типы для статистики

export type Period = "day" | "week" | "month";

export interface ActivityDataPoint {
  date: string;
  messages: number;
  users: number;
}

export interface DialogInfo {
  dialog_id: number;
  user_id: number;
  username: string | null;
  last_message_at: string;
  message_count: number;
  status?: string;
}

export interface UserActivity {
  user_id: number;
  username: string | null;
  message_count: number;
  percentage?: number;
}

export interface GeneralStats {
  total_messages: number;
  total_dialogs: number;
  active_users: number;
  avg_dialog_length?: number;
  total_messages_change?: number;
  total_dialogs_change?: number;
  active_users_change?: number;
  avg_dialog_length_change?: number;
}

export interface StatsResponse {
  period: Period;
  generated_at: string;
  general_stats: GeneralStats;
  activity_chart: Array<{
    time: string;
    messages: number;
  }>;
  top_users: Array<{
    user_display: string;
    message_count: number;
    percentage?: number;
  }>;
  recent_dialogs: Array<{
    user_display: string;
    message_count: number;
    last_active: string;
    status?: string;
  }>;
}
