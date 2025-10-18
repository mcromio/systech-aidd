"use client";

import { useEffect, useState, useCallback } from "react";
import type { Dialog } from "@/lib/chat-types";
import { chatApiClient } from "@/lib/chat-api";

interface UseDialogsResult {
  dialogs: Dialog[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useDialogs(userId: number): UseDialogsResult {
  const [dialogs, setDialogs] = useState<Dialog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchDialogs = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      const response = await chatApiClient.getDialogs(userId);
      setDialogs(response.dialogs);
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error("Failed to fetch dialogs")
      );
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    void fetchDialogs();
  }, [fetchDialogs]);

  return { dialogs, loading, error, refetch: fetchDialogs };
}

