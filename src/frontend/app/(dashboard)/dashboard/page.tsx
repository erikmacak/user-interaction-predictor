'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/layout/empty-state';
import { Button } from '@/components/ui/button';
import { formatDuration } from '@/lib/utils/format';
import { agentsApi, AgentResponse } from '@/lib/api/agents';

export default function DashboardPage() {
  const [auditingAgents, setAuditingAgents] = useState<AgentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await agentsApi.list('auditing');
        setAuditingAgents(data.agents);
      } catch (err: any) {
        setError('Failed to fetch auditing agents')
      } finally {
        setIsLoading(false);
      }
    };
    fetchAgents();
  }, []);

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

  if (auditingAgents.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <EmptyState
          title="No agent is currently operating"
          description="Once an agent starts auditing, it will appear here."
          action={
            <Link href="/agents">
              <Button>Manage Agents</Button>
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">System Overview</h1>
        <p className="mt-1 text-sm text-slate-600">
          Agents currently operating in the system
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {auditingAgents.map((agent) => (
          <Card key={agent.id}>
            <div className="space-y-2">
              <div>
                <p className="font-medium">{agent.name}</p>
                <p className="text-sm text-slate-600">{agent.platform}</p>
              </div>
              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-500">
                  Operating
                </p>
                <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                  Active
                </span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}