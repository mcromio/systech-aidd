"use client";

import type { GeneralStats } from "@/lib/types";

interface StatsCardsProps {
  stats: GeneralStats;
}

export function StatsCards({ stats }: StatsCardsProps) {
  const formatChange = (change: number) => {
    const symbol = change >= 0 ? "+" : "";
    const color = change >= 0 ? "text-green-600" : "text-red-600";
    return `${symbol}${change.toFixed(1)}%`;
  };

  const cards = [
    {
      title: "Total Dialogs",
      value: stats.total_dialogs.toLocaleString(),
      change: stats.total_dialogs_change,
    },
    {
      title: "Active Users",
      value: stats.active_users.toLocaleString(),
      change: stats.active_users_change,
    },
    {
      title: "Total Messages",
      value: stats.total_messages.toLocaleString(),
      change: stats.total_messages_change,
    },
    {
      title: "Avg Dialog Length",
      value: stats.avg_dialog_length.toFixed(1),
      change: stats.avg_dialog_length_change,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.title}
          className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
        >
          <h3 className="text-sm font-medium text-gray-600 mb-2">{card.title}</h3>
          <div className="flex items-end justify-between">
            <p className="text-2xl font-bold text-gray-900">{card.value}</p>
            <span
              className={`text-sm font-semibold ${
                card.change >= 0 ? "text-green-600" : "text-red-600"
              }`}
            >
              {formatChange(card.change)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
