"use client";

import { useState } from "react";
import type { Period } from "@/lib/types";
import { useStats } from "@/hooks/use-stats";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { ActivityChart } from "@/components/dashboard/activity-chart";
import { RecentDialogs } from "@/components/dashboard/recent-dialogs";
import { TopUsers } from "@/components/dashboard/top-users";

export default function DashboardPage() {
  const [period, setPeriod] = useState<Period>("day");
  const { data, loading, error } = useStats(period);

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 font-semibold mb-2">Error loading stats</p>
        <p className="text-gray-600 text-sm">{error.message}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Statistics and metrics for LLM assistant conversations</p>
        </div>

        {/* Period Selector */}
        <div className="flex gap-2">
          {(["day", "week", "month"] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                period === p
                  ? "bg-blue-500 text-white"
                  : "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
              }`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {loading && !data ? (
        <div className="flex items-center justify-center py-24">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="ml-3 text-gray-600">Loading stats...</p>
        </div>
      ) : null}

      {/* Content */}
      {data ? (
        <>
          <StatsCards stats={data.general_stats} />
          <ActivityChart data={data.activity_chart} period={period} />
          <RecentDialogs dialogs={data.recent_dialogs} />
          <TopUsers users={data.top_users} />

          {/* Metadata */}
          <div className="mt-8 text-center text-xs text-gray-500">
            <p>Data generated at: {new Date(data.generated_at).toLocaleString()}</p>
          </div>
        </>
      ) : null}
    </div>
  );
}
