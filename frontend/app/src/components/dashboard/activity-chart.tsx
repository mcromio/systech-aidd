"use client";

import type { Period } from "@/lib/types";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ActivityChartProps {
  data: Array<{ time: string; messages: number }>;
  period: Period;
}

export function ActivityChart({ data, period }: ActivityChartProps) {
  const getTitle = (period: Period) => {
    switch (period) {
      case "day":
        return "Activity by Hour";
      case "week":
        return "Activity by Day";
      case "month":
        return "Activity by Date";
      default:
        return "Activity";
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm mt-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">{getTitle(period)}</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: "12px" }} />
          <YAxis stroke="#6b7280" style={{ fontSize: "12px" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "6px",
            }}
          />
          <Line
            type="monotone"
            dataKey="messages"
            stroke="#3b82f6"
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
