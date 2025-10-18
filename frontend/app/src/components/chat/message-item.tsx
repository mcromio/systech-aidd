import { cn } from "@/lib/utils";
import type { MessageItem } from "@/lib/chat-types";
import { format, parseISO } from "date-fns";
import { ru } from "date-fns/locale";

interface MessageItemProps {
  message: MessageItem;
}

/**
 * Компонент для отображения одного сообщения в чате.
 *
 * @param message - Объект сообщения
 */
export function ChatMessageItem({ message }: MessageItemProps) {
  const isAssistant = message.role === "assistant";
  const timestamp = format(parseISO(message.created_at), "HH:mm", { locale: ru });

  return (
    <div
      className={cn(
        "flex w-full mb-4",
        isAssistant ? "justify-start" : "justify-end"
      )}
    >
      <div
        className={cn(
          "max-w-[70%] rounded-lg px-4 py-2",
          isAssistant
            ? "bg-muted text-foreground"
            : "bg-primary text-primary-foreground"
        )}
      >
        <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        <span className="text-xs opacity-70 mt-1 block">{timestamp}</span>
      </div>
    </div>
  );
}

