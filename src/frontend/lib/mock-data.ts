import { Agent, AuditSession, RunningAuditSession } from '@/types';

export const MOCK_AGENTS: Agent[] = [
  {
    id: 'a1',
    name: 'Alpha',
    platform: 'Instagram',
    state: 'auditing',
    predictorVersion: 'v1',
    checkVideoExistence: true,
  },
  {
    id: 'a2',
    name: 'Beta',
    platform: 'YouTube',
    state: 'offline',
    predictorVersion: 'v2',
    checkVideoExistence: false,
  },
  {
    id: 'a3',
    name: 'Gamma',
    platform: 'TikTok',
    state: 'banned',
    predictorVersion: 'v1',
    checkVideoExistence: true,
  },
];

export const MOCK_AUDIT_SESSIONS: AuditSession[] = [
  { id: 'audit_1', name: 'Audit session 1', agentId: 'a1' },
  { id: 'audit_2', name: 'Audit session 2', agentId: 'a2' },
  { id: 'audit_3', name: 'Audit session 3', agentId: 'a3' },
];

export const MOCK_RUNNING_AUDIT_SESSIONS: RunningAuditSession[] = [
  {
      id: 's1',
      agentId: 'a1',
      agentName: 'Alpha',
      startedAt: '10:00 AM',
      verificationKey: 'abc123xyz',
    },
    {
      id: 's2',
      agentId: 'a2',
      agentName: 'Beta',
      startedAt: '10:15 AM',
      verificationKey: 'def456uvw',
    },
    {
      id: 's3',
      agentId: 'a3',
      agentName: 'Gamma',
      startedAt: '10:30 AM',
      verificationKey: 'ghi789rst',
  }, 
]