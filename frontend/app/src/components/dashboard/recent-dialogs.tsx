"use client";

import type { DialogInfo } from "@/lib/types";

interface RecentDialogsProps {
  dialogs: DialogInfo[];
}

export function RecentDialogs({ dialogs }: RecentDialogsProps) {
  const getStatusBadge = (status: string) => {
    const statusClasses = {
      active: "bg-green-100 text-green-700",
      idle: "bg-yellow-100 text-yellow-700",
      inactive: "bg-gray-100 text-gray-700",
    };
    return statusClasses[status as keyof typeof statusClasses] || statusClasses.inactive;
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm mt-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Dialogs (Latest 10)</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="border-b border-gray-200">
            <tr>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">User</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Messages</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Last Active</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
            </tr>
          </thead>
          <tbody>
            {dialogs.map((dialog, idx) => (
              <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 text-gray-900 font-medium">{dialog.user_display}</td>
                <td className="py-3 px-4 text-gray-600">{dialog.message_count}</td>
                <td className="py-3 px-4 text-gray-600">{dialog.last_active}</td>
                <td className="py-3 px-4">
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(
                      dialog.status
                    )}`}
                  >
                    {dialog.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
