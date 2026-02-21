export type Platform = 'YouTube' | 'TikTok' | 'Instagram';
export type AgentState = 'auditing' | 'offline' | 'banned';

export interface Agent {
  id: string;
  name: string;
  platform: Platform;
  state: AgentState;
  predictorVersion: string;
  checkVideoExistence: boolean;
}

export interface AuditSession {
  id: string;
  name: string;
  agentId: string;
}

export interface RunningAuditSession {
  id: string;
  agentId: string;
  agentName: string;
  startedAt: string;
  verificationKey: string;
}