"use client";

import { useState } from "react";
import { useDialogs } from "@/hooks/use-dialogs";
import { useMessages } from "@/hooks/use-messages";
import { DialogsList } from "@/components/chat/dialogs-list";
import { MessageHistory } from "@/components/chat/message-history";
import { MessageInput } from "@/components/chat/message-input";

export default function ChatPage() {
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  // TODO: get actual userId from auth
  const { dialogs, loading, error } = useDialogs(1);
  const {
    messages,
    loading: messagesLoading,
    error: messagesError,
    refetch: refetchMessages,
  } = useMessages(selectedUserId);

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-4 p-4">
      {/* Sidebar - Список диалогов */}
      <div className="w-80 flex-shrink-0 rounded-lg border bg-card">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">Диалоги</h2>
        </div>
        <div className="overflow-y-auto" style={{ height: "calc(100% - 4rem)" }}>
          <DialogsList
            dialogs={dialogs}
            selectedUserId={selectedUserId}
            onSelectDialog={setSelectedUserId}
            loading={loading}
            error={error}
          />
        </div>
      </div>

      {/* Main - История сообщений */}
      <div className="flex-1 flex flex-col rounded-lg border bg-card">
        {selectedUserId ? (
          <>
            {/* Header */}
            <div className="p-4 border-b">
              <h2 className="text-lg font-semibold">
                Диалог с пользователем #{selectedUserId}
              </h2>
            </div>

            {/* Messages */}
            <div
              className="flex-1 overflow-hidden"
              style={{ height: "calc(100% - 8rem)" }}
            >
              <MessageHistory
                messages={messages}
                loading={messagesLoading}
                error={messagesError}
              />
            </div>

            {/* Input */}
            <MessageInput
              userId={selectedUserId}
              onMessageSent={() => void refetchMessages()}
            />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            Выберите диалог для просмотра
          </div>
        )}
      </div>
    </div>
  );
}

