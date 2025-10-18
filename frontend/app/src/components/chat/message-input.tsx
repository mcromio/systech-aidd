"use client";

import { useState, KeyboardEvent } from "react";
import { chatApiClient } from "@/lib/chat-api";

interface MessageInputProps {
  userId: number;
  onMessageSent: () => void;
}

/**
 * Компонент для ввода и отправки сообщений.
 *
 * @param userId - ID пользователя Telegram
 * @param onMessageSent - Callback после успешной отправки
 */
export function MessageInput({ userId, onMessageSent }: MessageInputProps) {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!text.trim() || sending) return;

    setSending(true);
    setError(null);

    try {
      await chatApiClient.sendMessage(userId, text.trim());
      setText("");
      onMessageSent();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className="border-t p-4">
      {error && (
        <div className="mb-2 text-sm text-destructive">
          Ошибка: {error}
        </div>
      )}
      <div className="flex gap-2">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Введите сообщение..."
          disabled={sending}
          className="flex-1 rounded-md border px-3 py-2 disabled:opacity-50"
        />
        <button
          onClick={() => void handleSend()}
          disabled={!text.trim() || sending}
          className="px-4 py-2 rounded-md bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90"
        >
          {sending ? "Отправка..." : "Отправить"}
        </button>
      </div>
    </div>
  );
}


