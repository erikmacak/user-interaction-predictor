import { apiClient } from './client';
import { Platform, AgentState } from '@/types';

export interface AgentCreateRequest {
  name: string;
  platform: Platform;
  predictor_version: string;
  state_file_data: string;
}

export interface AgentUpdateRequest {
  name?: string;
  platform?: Platform;
  predictor_version?: string;
  state?: AgentState;
  state_file_data?: string;
}

export interface AgentResponse {
  id: string;
  name: string;
  platform: Platform;
  state: AgentState;
  predictor_version: string;
  created_at: string;
  updated_at: string;
}

export interface AgentListResponse {
  agents: AgentResponse[];
  total: number;
}

interface PlatformsResponse {
  platforms: string[];
}

interface VersionsResponse {
  versions: string[];
}

export const agentsApi = {
  async getPlatforms(): Promise<string[]> {
    const response = await apiClient.get<PlatformsResponse>('/api/platforms');
    return response.platforms;
  },

  async getVersions(): Promise<string[]> {
    const response = await apiClient.get<VersionsResponse>('/api/predictor-versions');
    return response.versions;
  },

  async create(data: AgentCreateRequest): Promise<AgentResponse> {
    return apiClient.post<AgentResponse>('/api/agents', data);
  },

  async list(state?: string): Promise<AgentListResponse> {
    const endpoint = state ? `/api/agents?state=${state}` : '/api/agents';
    return apiClient.get<AgentListResponse>(endpoint);
  },

  async get(agentId: string): Promise<AgentResponse> {
    return apiClient.get<AgentResponse>(`/api/agents/${agentId}`);
  },

  async update(agentId: string, data: AgentUpdateRequest): Promise<AgentResponse> {
    return apiClient.put<AgentResponse>(`/api/agents/${agentId}`, data);
  },

  async delete(agentId: string): Promise<void> {
    return apiClient.delete<void>(`/api/agents/${agentId}`);
  },
} as const;