"use client";

interface TopUsersProps {
  users: Array<{
    user_display: string;
    message_count: number;
    percentage?: number;
  }>;
}

export function TopUsers({ users }: TopUsersProps) {
  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm mt-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Users (Top 5)</h2>
      <div className="space-y-4">
        {users.map((user, idx) => (
          <div key={idx} className="flex items-center gap-4">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <p className="font-medium text-gray-900">{user.user_display}</p>
                <span className="text-sm font-semibold text-gray-600">{user.percentage?.toFixed(1) || "0"}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${user.percentage || 0}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">{user.message_count} messages</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
