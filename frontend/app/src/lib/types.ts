// Типы для статистики

export type Period = "day" | "week" | "month";

export interface StatsResponse {
  period: Period;
  total_messages: number;
  total_users: number;
  total_dialogs: number;
  active_users_count: number;
  messages_by_date: Array<{
    date: string;
    count: number;
  }>;
  top_users: Array<{
    user_id: number;
    username: string;
    message_count: number;
  }>;
  dialogs_activity: Array<{
    dialog_id: number;
    message_count: number;
    last_activity: string;
  }>;
}
