export type Platform = 'YouTube' | 'TikTok' | 'Instagram';
export type AgentState = 'auditing' | 'offline' | 'banned';
export type SessionState = 'running' | 'completed';

export interface Agent {
  id: string;
  name: string;
  platform: Platform;
  state: AgentState;
  predictorVersion: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuditSession {
  id: string;
  agentId: string;
  agentName: string;
  agentPlatform: Platform;
  state: SessionState;
  startedAt: string;
  endedAt: string | null;
}