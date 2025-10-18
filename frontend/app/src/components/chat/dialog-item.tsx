import type { Dialog } from "@/lib/chat-types";
import { cn } from "@/lib/utils";

interface DialogItemProps {
  dialog: Dialog;
  isSelected: boolean;
  onClick: () => void;
}

export function DialogItem({ dialog, isSelected, onClick }: DialogItemProps) {
  const displayName =
    dialog.first_name && dialog.last_name
      ? `${dialog.first_name} ${dialog.last_name}`
      : dialog.first_name || dialog.username || `User #${dialog.user_id}`;

  const lastMessagePreview = dialog.last_message
    ? dialog.last_message.text.substring(0, 50) + (dialog.last_message.text.length > 50 ? "..." : "")
    : "Нет сообщений";

  const lastMessageTime = dialog.last_message
    ? new Date(dialog.last_message.timestamp).toLocaleTimeString("ru-RU", {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  return (
    <div
      className={cn(
        "p-4 border-b cursor-pointer hover:bg-accent transition-colors",
        isSelected && "bg-accent"
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <h3 className="font-semibold truncate">{displayName}</h3>
            {lastMessageTime && (
              <span className="text-xs text-muted-foreground flex-shrink-0">
                {lastMessageTime}
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground truncate">
            {lastMessagePreview}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-muted-foreground">
              {dialog.total_messages || 0} сообщений
            </span>
            {dialog.unread_count > 0 && (
              <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded-full">
                {dialog.unread_count}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

