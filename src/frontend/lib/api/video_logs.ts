import { apiClient } from './client';

export interface SessionData {
  session_id: string;
  date: string;
  video_count: number;
}

export const videoLogsApi = {
  async getAgentSessions(agentId: string): Promise<SessionData[]> {
    return apiClient.get<SessionData[]>(`/api/agents/${agentId}/sessions`);
  },

  async downloadSessionData(agentId: string, sessionId: string): Promise<Blob> {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || ''}/api/agents/${agentId}/sessions/${sessionId}/export`,
      {
        method: 'GET',
        credentials: 'include',
      }
    );

    if (!response.ok) {
      throw new Error('Failed to download session data');
    }

    return response.blob();
  },

  async downloadAllData(agentId: string): Promise<Blob> {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || ''}/api/agents/${agentId}/export`,
      {
        method: 'GET',
        credentials: 'include',
      }
    );

    if (!response.ok) {
      throw new Error('Failed to download all data');
    }

    return response.blob();
  },
};