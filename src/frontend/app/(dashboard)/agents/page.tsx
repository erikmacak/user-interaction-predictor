'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MOCK_AGENTS } from '@/lib/mock-data';
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

const STATE_STYLES = {
  auditing: 'bg-green-100 text-green-700',
  offline: 'bg-slate-100 text-slate-700',
  banned: 'bg-red-100 text-red-700',
};

export default function AgentsPage() {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [agentToDelete, setAgentToDelete] = useState<string | null>(null);

  const handleDeleteClick = (agentId: string, agentName: string) => {
    setAgentToDelete(agentId);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    setDeleteDialogOpen(false);
    setAgentToDelete(null);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setAgentToDelete(null);
  };

  const selectedAgent = MOCK_AGENTS.find((a) => a.id === agentToDelete);

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
          {MOCK_AGENTS.map((agent) => (
            <Card key={agent.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle>{agent.name}</CardTitle>
                    <CardDescription className="mt-1">
                      {agent.platform} • {agent.predictorVersion}
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
                    onClick={() => handleDeleteClick(agent.id, agent.name)}
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
              <strong>{selectedAgent?.name}</strong>? This action cannot be
              undone and all associated audit data will be permanently removed.
            </DialogDescription>
          </DialogHeader>

          <DialogFooter>
            <Button variant="secondary" onClick={handleDeleteCancel}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDeleteConfirm}>
              Delete Agent
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}