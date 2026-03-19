'use client';

import { useState, useEffect } from 'react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { EmptyState } from '@/components/layout/empty-state';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { agentsApi, AgentResponse } from '@/lib/api/agents';
import { 
  auditSessionsApi, 
  AuditSessionResponse 
} from '@/lib/api/audit_sessions';
import { format } from 'date-fns';

export default function SessionsPage() {
  const [agents, setAgents] = useState<AgentResponse[]>([]);
  const [runningSessions, setRunningSessions] = useState<AuditSessionResponse[]>([]);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingAgents, setIsLoadingAgents] = useState(true);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedSessionId, setCopiedSessionId] = useState<string | null>(null);

  const fetchAgents = async () => {
    setIsLoadingAgents(true);
    try {
      const data = await agentsApi.list('offline');
      setAgents(data.agents);
    } catch (err: any) {
      setError('Failed to fetch offline agents');
    } finally {
      setIsLoadingAgents(false);
    }
  };

  const fetchRunningSessions = async () => {
    setIsLoadingSessions(true);
    try {
      const data = await auditSessionsApi.listRunning();
      setRunningSessions(data.sessions);
    } catch (err: any) {
      setError('Failed to fetch running sessions');
    } finally {
      setIsLoadingSessions(false);
    }
  };

  useEffect(() => {
    fetchAgents();
    fetchRunningSessions();
    setIsLoading(false);
  }, []);

  const isFormValid = selectedAgent.length > 0;

  const handleStartSession = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedAgent) return;

    setIsStarting(true);
    setError(null);

    try {
      await auditSessionsApi.start({ agent_id: selectedAgent });
      
      await Promise.all([fetchAgents(), fetchRunningSessions()]);
      
      setSelectedAgent('');
    } catch (err: any) {
      setError(err.message || 'Failed to start session');
    } finally {
      setIsStarting(false);
    }
  };

  const handleEndSession = async (sessionId: string) => {
    try {
      await auditSessionsApi.stop(sessionId);
      
      await Promise.all([fetchAgents(), fetchRunningSessions()]);
    } catch (err: any) {
      setError(err.message || 'Failed to stop session');
    }
  };

  const handleCopySessionId = async (sessionId: string) => {
    try {
      await navigator.clipboard.writeText(sessionId);
      setCopiedSessionId(sessionId);
      setTimeout(() => setCopiedSessionId(null), 2000);
    } catch (err) {
      setError('Failed to copy session ID');
    }
  };

  const formatStartTime = (dateString: string) => {
    const date = new Date(dateString);
    date.setHours(date.getHours() + 1);
    return format(date, 'HH:mm');
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <EmptyState
          title="Loading system overview"
          description="Please wait while we load system configuration"
        />
      </div>
    );
  }

  if (error && agents.length === 0 && runningSessions.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="mt-1 text-sm text-slate-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Sessions</h1>
        <p className="mt-1 text-sm text-slate-600">
          Manage audit sessions and monitoring
        </p>
        <p className="mt-4 text-sm text-slate-600">
          Once the session starts, copy the Session ID and assign it to the agent
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-md bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">Start New Session</CardTitle>
          <CardDescription className="text-xs">
            Select an offline agent to begin an audit session
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleStartSession} className="space-y-3">
          <Select
            label="Select Agent"
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            disabled={isLoadingAgents || isStarting}
          >
            <option value="" disabled>
              {isLoadingAgents 
                ? 'Loading agents...' 
                : agents.length === 0 
                ? 'No offline agents available'
                : 'Choose an agent...'}
            </option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} ({agent.platform})
              </option>
            ))}
          </Select>

          <Button 
            type="submit" 
            className="w-full" 
            disabled={!isFormValid || isStarting || isLoadingAgents}
          >
            {isStarting ? 'Starting...' : 'Start Session'}
          </Button>
        </form>
      </Card>

      <div className="relative mb-6">
        <div className="h-px bg-slate-300" />
        <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-50 px-3 text-xs font-medium text-slate-500">
          Active Sessions
        </span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Running Sessions</CardTitle>
          <CardDescription className="text-xs">
            {isLoadingSessions
              ? 'Loading sessions...'
              : runningSessions.length === 0
              ? 'No active sessions'
              : `${runningSessions.length} active session(s)`}
          </CardDescription>
        </CardHeader>

        <div className="border-t border-slate-200">
          {isLoadingSessions ? (
            <div className="flex items-center justify-center p-8 text-center">
              <div>
                <p className="text-sm font-medium text-slate-900">
                  Loading sessions...
                </p>
              </div>
            </div>
          ) : runningSessions.length === 0 ? (
            <div className="flex items-center justify-center p-8 text-center">
              <div>
                <p className="text-sm font-medium text-slate-900">
                  No active sessions
                </p>
                <p className="mt-1 text-xs text-slate-600">
                  Start a session to begin auditing
                </p>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-slate-200">
              {runningSessions.map((session) => (
                <div
                  key={session.id}
                  className="p-4 transition-colors hover:bg-slate-50"
                >
                  <div className="hidden md:block">
                    <div className="mb-2 flex items-start justify-between">
                      <p className="font-medium text-slate-900">
                        {session.agent_name}
                      </p>
                      <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                        Running
                      </span>
                    </div>
                    
                    <p className="mb-2 text-xs text-slate-600">
                      {session.agent_platform} • Started at {formatStartTime(session.started_at)}
                    </p>
                    
                    <div className="flex items-center gap-2">
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => handleCopySessionId(session.id)}
                        className="h-8 px-3 text-xs"
                      >
                        {copiedSessionId === session.id ? 'Copied!' : 'Copy Session ID'}
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => handleEndSession(session.id)}
                        className="h-8 px-3 text-xs"
                      >
                        Stop Session
                      </Button>
                    </div>
                  </div>

                  <div className="md:hidden">
                    <div className="mb-2 flex items-start justify-between">
                      <p className="font-medium text-slate-900">
                        {session.agent_name}
                      </p>
                      <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                        Running
                      </span>
                    </div>
                    
                    <p className="mb-3 text-xs text-slate-600">
                      {session.agent_platform} • Started at {formatStartTime(session.started_at)}
                    </p>
                    
                    <div className="flex gap-2">
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => handleCopySessionId(session.id)}
                        className="flex-1 text-xs"
                      >
                        {copiedSessionId === session.id ? 'Copied!' : 'Copy Session ID'}
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => handleEndSession(session.id)}
                        className="flex-1 text-xs"
                      >
                        Stop
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}