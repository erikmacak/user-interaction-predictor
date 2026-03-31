'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/layout/empty-state';
import { Button } from '@/components/ui/button';
import { agentsApi, AgentResponse } from '@/lib/api/agents';

const PAGE_TEXT = {
  HEADING: 'System Overview',
  DESCRIPTION: 'Agents currently operating in the system',
  EMPTY_TITLE: 'No agent is currently operating',
  EMPTY_DESCRIPTION: 'Once an agent starts auditing, it will appear here.',
  BUTTON_MANAGE: 'Manage Agents',
  STATUS_OPERATING: 'Operating',
  BADGE_ACTIVE: 'Active',
  LOADING_TITLE: 'Loading system overview',
  LOADING_DESCRIPTION: 'Please wait while we load system configuration',
} as const;

const ROUTES = {
  AGENTS: '/agents',
} as const;

const STYLES = {
  BADGE: 'inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700',
} as const;

export default function DashboardPage() {
  const [auditingAgents, setAuditingAgents] = useState<AgentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    try {
      const data = await agentsApi.list('auditing');
      setAuditingAgents(data.agents);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <EmptyState
          title={PAGE_TEXT.LOADING_TITLE}
          description={PAGE_TEXT.LOADING_DESCRIPTION}
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-medium text-slate-900">
            Error! Something went wrong.
          </h2>
          <p className="mt-1 text-sm text-slate-600">{error}</p>
        </div>
      </div>
    );
  }

  if (auditingAgents.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <EmptyState
          title={PAGE_TEXT.EMPTY_TITLE}
          description={PAGE_TEXT.EMPTY_DESCRIPTION}
          action={
            <Link href={ROUTES.AGENTS}>
              <Button>{PAGE_TEXT.BUTTON_MANAGE}</Button>
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">{PAGE_TEXT.HEADING}</h1>
        <p className="mt-1 text-sm text-slate-600">{PAGE_TEXT.DESCRIPTION}</p>
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
                <p className="text-xs text-slate-500">{PAGE_TEXT.STATUS_OPERATING}</p>
                <span className={STYLES.BADGE}>{PAGE_TEXT.BADGE_ACTIVE}</span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}