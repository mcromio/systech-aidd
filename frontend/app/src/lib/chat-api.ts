// API client для работы с чатом

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const chatApiClient = {
  async getDialogs(userId: number) {
    const response = await fetch(`${API_BASE_URL}/api/v1/users/${userId}/dialogs`);
    if (!response.ok) {
      throw new Error(`Failed to fetch dialogs: ${response.statusText}`);
    }
    return response.json();
  },

  async getMessages(userId: number, dialogId: number) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/users/${userId}/dialogs/${dialogId}/messages`
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch messages: ${response.statusText}`);
    }
    return response.json();
  },

  async sendMessage(userId: number, dialogId: number, content: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/users/${userId}/dialogs/${dialogId}/messages`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content }),
      }
    );
    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`);
    }
    return response.json();
  },
};
