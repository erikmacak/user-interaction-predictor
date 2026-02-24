'use client';

import { useState, useEffect } from 'react';
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

const STATE_STYLES = {
  auditing: 'bg-green-100 text-green-700',
  offline: 'bg-slate-100 text-slate-700',
  banned: 'bg-red-100 text-red-700',
};

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [agentToDelete, setAgentToDelete] = useState<AgentResponse | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchAgents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await agentsApi.list();
      setAgents(data.agents);
    } catch (err: any) {
      setError('Failed to load agents');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleDeleteClick = (agent: AgentResponse) => {
    setAgentToDelete(agent);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!agentToDelete) return;

    setIsDeleting(true);
    try {
      await agentsApi.delete(agentToDelete.id);
      await fetchAgents();
      setDeleteDialogOpen(false);
      setAgentToDelete(null);
    } catch (err: any) {
      setError('Failed to delete agent');
      setDeleteDialogOpen(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setAgentToDelete(null);
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
          <Button onClick={fetchAgents} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div>
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Agents</h1>
            <p className="mt-1 text-sm text-slate-600">
              Manage your auditing agents
            </p>
          </div>
          <Link href="/agents/new">
            <Button>Add Agent</Button>
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
                    <Link href={`/agents/${agent.id}/edit`} className="flex-1">
                      <Button variant="primary" className="w-full">
                        Edit
                      </Button>
                    </Link>
                    <Button
                      variant="danger"
                      className="flex-1"
                      onClick={() => handleDeleteClick(agent)}
                    >
                      Delete
                    </Button>
                  </div>
                  <Link
                    href={`/agents/${agent.id}/audit-data`}
                    className="block"
                  >
                    <Button variant="secondary" className="w-full">
                      Data
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
            <DialogTitle>Delete Agent</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete{' '}
              <strong>{agentToDelete?.name}</strong>? This action cannot be
              undone and all associated audit data will be permanently removed.
            </DialogDescription>
          </DialogHeader>

          <DialogFooter>
            <Button 
              variant="secondary" 
              onClick={handleDeleteCancel}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button 
              variant="danger" 
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
            >
              {isDeleting ? 'Deleting...' : 'Delete Agent'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}