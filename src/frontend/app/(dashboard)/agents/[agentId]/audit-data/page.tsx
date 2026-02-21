'use client';

import { use, useState } from 'react';
import { MOCK_AUDIT_SESSIONS } from '@/lib/mock-data';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';

interface PageProps {
  params: Promise<{ agentId: string }>;
}

export default function AuditDataPage({ params }: PageProps) {
  const { agentId } = use(params);
  const sessions = MOCK_AUDIT_SESSIONS.filter((s) => s.agentId === agentId);
  const [selectedSession, setSelectedSession] = useState(sessions[0]?.id || '');

  const handleDownload = (downloadAll: boolean = false) => {
    
  };

  if (sessions.length === 0) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-medium text-slate-900">
            No audit sessions found
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            This agent doesn't have any audit sessions yet.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Download Audit Data</CardTitle>
          <CardDescription>
            Download collected audit data for this agent
          </CardDescription>
        </CardHeader>

        <div className="space-y-4">
          <Select
            label="Select Audit Session"
            value={selectedSession}
            onChange={(e) => setSelectedSession(e.target.value)}
          >
            {sessions.map((session) => (
              <option key={session.id} value={session.id}>
                {session.name}
              </option>
            ))}
          </Select>

          <div className="space-y-2">
            <Button
              onClick={() => handleDownload(false)}
              className="w-full"
              disabled={!selectedSession}
            >
              Download Selected Session
            </Button>

            <Button
              onClick={() => handleDownload(true)}
              variant="secondary"
              className="w-full"
            >
              Download All Sessions
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}