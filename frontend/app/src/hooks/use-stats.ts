"use client";

import { useEffect, useState, useCallback } from "react";
import type { Period, StatsResponse } from "@/lib/types";
import { apiClient } from "@/lib/api";

interface UseStatsResult {
  data: StatsResponse | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useStats(period: Period = "day"): UseStatsResult {
  const [data, setData] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchStats = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiClient.getStats(period);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch stats"));
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    void fetchStats();
  }, [fetchStats]);

  return { data, loading, error, refetch: fetchStats };
}
