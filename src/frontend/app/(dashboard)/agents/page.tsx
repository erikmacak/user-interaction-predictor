'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { cn } from '@/lib/utils/cn';
import { agentsApi, AgentResponse } from '@/lib/api/agents';
import { EmptyState } from '@/components/layout/empty-state';
import { AgentState } from '@/types';

const STATE_STYLES: Record<AgentState, string> = {
  auditing: 'bg-green-100 text-green-700',
  offline: 'bg-slate-100 text-slate-700',
  banned: 'bg-red-100 text-red-700',
} as const;

const PAGE_TEXT = {
  HEADING: 'Agents',
  DESCRIPTION: 'Manage your auditing agents',
  BUTTON_ADD: 'Add Agent',
  BUTTON_EDIT: 'Edit',
  BUTTON_DELETE: 'Delete',
  BUTTON_DATA: 'Data',
  DIALOG_TITLE: 'Delete Agent',
  DIALOG_DESCRIPTION_PREFIX: 'Are you sure you want to delete',
  DIALOG_DESCRIPTION_SUFFIX:
    '? This action cannot be undone and all associated audit data will be permanently removed.',
  BUTTON_CANCEL: 'Cancel',
  BUTTON_CONFIRM: 'Delete Agent',
  BUTTON_DELETING: 'Deleting...',
  LOADING_TITLE: 'Loading system overview',
  LOADING_DESCRIPTION: 'Please wait while we load system configuration',
} as const;

const ROUTES = {
  NEW_AGENT: '/agents/new',
  EDIT_AGENT: (id: string) => `/agents/${id}/edit`,
  AUDIT_DATA: (id: string) => `/agents/${id}/audit-data`,
} as const;

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [agentToDelete, setAgentToDelete] = useState<AgentResponse | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchAgents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await agentsApi.list();
      setAgents(data.agents);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const handleDeleteClick = useCallback((agent: AgentResponse) => {
    setAgentToDelete(agent);
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = async () => {
    if (!agentToDelete) return;

    setIsDeleting(true);
    try {
      await agentsApi.delete(agentToDelete.id);
      await fetchAgents();
      setDeleteDialogOpen(false);
      setAgentToDelete(null);
    } catch (err: any) {
      setError(err.message);
      setDeleteDialogOpen(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
    setAgentToDelete(null);
  }, []);

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

  return (
    <>
      <div>
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">{PAGE_TEXT.HEADING}</h1>
            <p className="mt-1 text-sm text-slate-600">{PAGE_TEXT.DESCRIPTION}</p>
          </div>
          <Link href={ROUTES.NEW_AGENT}>
            <Button>{PAGE_TEXT.BUTTON_ADD}</Button>
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <Card key={agent.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle>{agent.name}</CardTitle>
                    <CardDescription className="mt-1">
                      {agent.platform} • {agent.predictor_version}
                    </CardDescription>
                  </div>
                  <span
                    className={cn(
                      'inline-flex items-center rounded-full px-2 py-1 text-xs font-medium',
                      STATE_STYLES[agent.state]
                    )}
                  >
                    {agent.state}
                  </span>
                </div>
              </CardHeader>

              <div className="mt-4 space-y-2">
                <div className="flex gap-2">
                  <Link href={ROUTES.EDIT_AGENT(agent.id)} className="flex-1">
                    <Button variant="primary" className="w-full">
                      {PAGE_TEXT.BUTTON_EDIT}
                    </Button>
                  </Link>
                  <Button
                    variant="danger"
                    className="flex-1"
                    onClick={() => handleDeleteClick(agent)}
                  >
                    {PAGE_TEXT.BUTTON_DELETE}
                  </Button>
                </div>
                <Link href={ROUTES.AUDIT_DATA(agent.id)} className="block">
                  <Button variant="secondary" className="w-full">
                    {PAGE_TEXT.BUTTON_DATA}
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </div>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{PAGE_TEXT.DIALOG_TITLE}</DialogTitle>
            <DialogDescription>
              {PAGE_TEXT.DIALOG_DESCRIPTION_PREFIX}{' '}
              <strong>{agentToDelete?.name}</strong>
              {PAGE_TEXT.DIALOG_DESCRIPTION_SUFFIX}
            </DialogDescription>
          </DialogHeader>

          <DialogFooter>
            <Button
              variant="secondary"
              onClick={handleDeleteCancel}
              disabled={isDeleting}
            >
              {PAGE_TEXT.BUTTON_CANCEL}
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
            >
              {isDeleting ? PAGE_TEXT.BUTTON_DELETING : PAGE_TEXT.BUTTON_CONFIRM}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}