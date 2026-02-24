'use client';

import { useState, useEffect } from 'react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { agentsApi, AgentResponse } from '@/lib/api/agents';
import { EmptyState } from '@/components/layout/empty-state';

export default function SessionsPage() {
  const [agents, setAgents] = useState<AgentResponse[]>([]);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await agentsApi.list('offline');
        setAgents(data.agents);
      } catch (err: any) {
        setError('Failed to fetch available agents')
      } finally {
        setIsLoading(false);
      }
    };
    fetchAgents();
  }, []);

  const isFormValid = selectedAgent.length > 0;

  const handleStartSession = (e: React.FormEvent) => {
    e.preventDefault();
    
  };

  const handleEndSession = (sessionId: string, agentName: string) => {
    
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

  if (error) {
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
          Manage audit sessions and verification keys
        </p>
      </div>

      <div className="mb-6 space-y-2">
        <p className="text-sm text-slate-600">
          • Once a session is started, a verification key is generated and must
          be included in the agent's HTTP request.
        </p>
        <p className="text-sm text-slate-600">
          • Sessions can be stopped at any time to revoke access.
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">Start New Session</CardTitle>
          <CardDescription className="text-xs">
            Select an agent to begin an audit session
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleStartSession} className="space-y-3">
          <Select
            label="Select Agent"
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            disabled={isLoading}
          >
            <option value="" disabled>
              {isLoading ? 'Loading agents...' : 'Choose an agent...'}
            </option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} ({agent.platform})
              </option>
            ))}
          </Select>

          <Button type="submit" className="w-full" disabled={!isFormValid || isLoading}>
            Start Session
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
            No active sessions
          </CardDescription>
        </CardHeader>

        <div className="border-t border-slate-200">
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
        </div>
      </Card>
    </div>
  );
}