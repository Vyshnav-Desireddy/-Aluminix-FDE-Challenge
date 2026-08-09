const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Tasks
  getTasks: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${API_BASE_URL}/api/tasks?${params}`);
    if (!response.ok) throw new Error('Failed to fetch tasks');
    return response.json();
  },

  // Stats
  getStats: async () => {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },

  // Ingest
  ingestEmail: async (emailData) => {
    const response = await fetch(`${API_BASE_URL}/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(emailData),
    });
    if (!response.ok) throw new Error('Failed to ingest email');
    return response.json();
  },

  // Chat
  chat: async (message) => {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });
    if (!response.ok) throw new Error('Failed to send chat message');
    return response.json();
  },
};
