import { apiClient } from './client';

export interface AuditSessionStartRequest {
  agent_id: string;
}

export interface AuditSessionResponse {
  id: string;
  agent_id: string;
  agent_name: string;
  agent_platform: string;
  state: string;
  started_at: string;
  ended_at: string | null;
}

export interface AuditSessionListResponse {
  sessions: AuditSessionResponse[];
  total: number;
}

export const auditSessionsApi = {
  async start(agentId: string): Promise<AuditSessionResponse> {
    return apiClient.post<AuditSessionResponse>('/api/sessions', {
      agent_id: agentId,
    });
  },

  async listRunning(): Promise<AuditSessionListResponse> {
    return apiClient.get<AuditSessionListResponse>('/api/sessions/running');
  },

  async stop(sessionId: string): Promise<void> {
    return apiClient.post<void>(`/api/sessions/${sessionId}/stop`, {});
  },
} as const;