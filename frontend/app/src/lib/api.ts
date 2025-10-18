// API client для работы со статистикой

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = {
  async getStats(period: string = "day") {
    const response = await fetch(`${API_BASE_URL}/api/v1/stats?period=${period}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
  },
};
