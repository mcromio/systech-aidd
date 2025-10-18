"use client";

import { useEffect, useState, useCallback } from "react";
import { chatApiClient } from "@/lib/chat-api";
import type { MessageItem } from "@/lib/chat-types";

interface UseMessagesResult {
  messages: MessageItem[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

/**
 * React hook для получения истории сообщений с автообновлением.
 *
 * Автоматически обновляет историю каждые 3 секунды для синхронизации
 * сообщений между веб-интерфейсом и Telegram.
 *
 * @param userId - ID пользователя Telegram
 * @returns Объект с сообщениями, состоянием загрузки, ошибкой и функцией перезагрузки
 */
export function useMessages(userId: number | null, dialogId?: number): UseMessagesResult {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchMessages = useCallback(async () => {
    if (userId === null || dialogId === undefined) {
      setMessages([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await chatApiClient.getMessages(userId, dialogId);
      setMessages(response.messages);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [userId, dialogId]);

  useEffect(() => {
    void fetchMessages();

    // Автообновление каждые 3 секунды для синхронизации с Telegram
    if (userId !== null && dialogId !== undefined) {
      const interval = setInterval(() => {
        void fetchMessages();
      }, 3000);

      return () => clearInterval(interval);
    }

    // Явный return undefined для TypeScript
    return undefined;
  }, [fetchMessages, userId, dialogId]);

  return { messages, loading, error, refetch: fetchMessages };
}

