import type { Dialog } from "@/lib/chat-types";
import { DialogItem } from "./dialog-item";

interface DialogsListProps {
  dialogs: Dialog[];
  selectedUserId: number | null;
  onSelectDialog: (userId: number) => void;
  loading: boolean;
  error: Error | null;
}

export function DialogsList({
  dialogs,
  selectedUserId,
  onSelectDialog,
  loading,
  error,
}: DialogsListProps) {
  if (loading) {
    return (
      <div className="p-4 text-center text-muted-foreground">
        Загрузка диалогов...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-destructive">
        Ошибка: {error.message}
      </div>
    );
  }

  if (dialogs.length === 0) {
    return (
      <div className="p-4 text-center text-muted-foreground">
        Нет диалогов
      </div>
    );
  }

  return (
    <div>
      {dialogs.map((dialog) => (
        <DialogItem
          key={dialog.user_id}
          dialog={dialog}
          isSelected={selectedUserId === dialog.user_id}
          onClick={() => onSelectDialog(dialog.user_id)}
        />
      ))}
    </div>
  );
}

