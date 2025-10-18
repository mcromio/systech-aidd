// API client для работы с чатом

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const chatApiClient = {
  async getDialogs() {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/dialogs`);
    if (!response.ok) {
      throw new Error(`Failed to fetch dialogs: ${response.statusText}`);
    }
    return response.json();
  },

  async getMessages(userId: number, limit: number = 50, offset: number = 0) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/chat/dialogs/${userId}/messages?limit=${limit}&offset=${offset}`
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch messages: ${response.statusText}`);
    }
    return response.json();
  },

  async sendMessage(userId: number, content: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/chat/dialogs/${userId}/send`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: content }),
      }
    );
    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`);
    }
    return response.json();
  },
};
