"use client";

import { useEffect, useRef } from "react";
import { ChatMessageItem } from "./message-item";
import type { MessageItem } from "@/lib/chat-types";

interface MessageHistoryProps {
  messages: MessageItem[];
  loading: boolean;
  error: Error | null;
}

/**
 * Компонент для отображения истории сообщений с автопрокруткой.
 *
 * @param messages - Массив сообщений
 * @param loading - Флаг загрузки
 * @param error - Объект ошибки
 */
export function MessageHistory({ messages, loading, error }: MessageHistoryProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Автопрокрутка к последнему сообщению
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        Загрузка сообщений...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-destructive">
        Ошибка загрузки сообщений: {error.message}
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        Сообщений пока нет. Начните диалог!
      </div>
    );
  }

  return (
    <div className="flex flex-col p-4 overflow-y-auto h-full">
      {messages.map((message) => (
        <ChatMessageItem key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}

