'use client';

import { useState } from 'react';
import { MOCK_AGENTS, MOCK_RUNNING_AUDIT_SESSIONS } from '@/lib/mock-data';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';

export default function SessionsPage() {
  const [selectedAgent, setSelectedAgent] = useState('');

  const isFormValid = selectedAgent.length > 0;

  const handleStartSession = (e: React.FormEvent) => {
    e.preventDefault();
  };

  const handleEndSession = (sessionId: string, agentName: string) => {

  };

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
          >
            <option value="" disabled>
              Choose an agent...
            </option>
            {MOCK_AGENTS.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} ({agent.platform})
              </option>
            ))}
          </Select>

          <Button type="submit" className="w-full" disabled={!isFormValid}>
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
            {MOCK_RUNNING_AUDIT_SESSIONS.length === 0
              ? 'No active sessions'
              : `${MOCK_RUNNING_AUDIT_SESSIONS.length} active session(s)`}
          </CardDescription>
        </CardHeader>

        <div className="border-t border-slate-200">
          {MOCK_RUNNING_AUDIT_SESSIONS.length === 0 ? (
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
              {MOCK_RUNNING_AUDIT_SESSIONS.map((session) => (
                <div
                  key={session.id}
                  className="flex items-center justify-between p-4 transition-colors hover:bg-slate-50"
                >
                  <div className="flex-1">
                    <p className="font-medium text-slate-900">
                      {session.agentName}
                    </p>
                    <p className="mt-0.5 text-xs text-slate-600">
                      Started at: {session.startedAt}
                    </p>
                    <div className="mt-2 flex items-center gap-2">
                      <span className="text-xs font-medium text-slate-700">
                        Key:
                      </span>
                      <code className="rounded bg-slate-100 px-2 py-0.5 text-xs font-mono text-slate-800">
                        {session.verificationKey}
                      </code>
                    </div>
                  </div>
                  <Button
                    variant="danger"
                    onClick={() =>
                      handleEndSession(session.id, session.agentName)
                    }
                    className="ml-4"
                  >
                    End Session
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}