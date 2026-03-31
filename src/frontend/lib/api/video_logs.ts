import { apiClient } from './client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SessionData {
  session_id: string;
  date: string;
  video_count: number;
}

async function downloadFile(url: string, errorMessage: string): Promise<Blob> {
  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(errorMessage);
  }

  return response.blob();
}

export const videoLogsApi = {
  async getAgentSessions(agentId: string): Promise<SessionData[]> {
    return apiClient.get<SessionData[]>(`/api/agents/${agentId}/sessions`);
  },

  async downloadSessionData(agentId: string, sessionId: string): Promise<Blob> {
    const url = `${API_BASE_URL}/api/agents/${agentId}/sessions/${sessionId}/export`;
    return downloadFile(url, 'Failed to download session data');
  },

  async downloadAllData(agentId: string): Promise<Blob> {
    const url = `${API_BASE_URL}/api/agents/${agentId}/export`;
    return downloadFile(url, 'Failed to download all data');
  },
} as const;