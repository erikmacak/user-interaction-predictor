'use client';

import { use, useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { videoLogsApi, SessionData } from '@/lib/api/video_logs';

interface PageProps {
  params: Promise<{ agentId: string }>;
}

export default function AuditDataPage({ params }: PageProps) {
  const { agentId } = use(params);
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [selectedSession, setSelectedSession] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSessions();
  }, [agentId]);

  const fetchSessions = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const sessionsData = await videoLogsApi.getAgentSessions(agentId);
      setSessions(sessionsData);
      
      if (sessionsData.length > 0) {
        setSelectedSession(sessionsData[0].session_id);
      }
    } catch (err: any) {
      console.error('Failed to load sessions:', err);
      setError('Failed to load audit sessions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (downloadAll: boolean = false) => {
    setIsDownloading(true);
    
    try {
      if (downloadAll) {
        const blob = await videoLogsApi.downloadAllData(agentId);
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `agent_${agentId}_all_data.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        if (!selectedSession) return;
        
        const blob = await videoLogsApi.downloadSessionData(agentId, selectedSession);
        
        const session = sessions.find((s) => s.session_id === selectedSession);
        const filename = session 
          ? `session_${session.date.replace(/-/g, '')}_data.csv`
          : `session_${selectedSession}_data.csv`;
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err: any) {
      console.error('Download failed:', err);
      setError('Failed to download data');
    } finally {
      setIsDownloading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-medium text-slate-900">
            Loading...
          </h2>
        </div>
      </div>
    );
  }

  if (error && sessions.length === 0) {
    return (
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <Link href="/agents">
            <Button variant="secondary">← Back to Agents</Button>
          </Link>
        </div>
        
        <div className="flex min-h-[60vh] items-center justify-center">
          <div className="text-center">
            <h2 className="text-lg font-medium text-slate-900">
              Error
            </h2>
            <p className="mt-1 text-sm text-slate-600">{error}</p>
            <Button onClick={fetchSessions} className="mt-4">
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <Link href="/agents">
            <Button variant="secondary">← Back to Agents</Button>
          </Link>
        </div>
        
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
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Select Audit Session
            </label>
            <Select
              value={selectedSession}
              onChange={(e) => setSelectedSession(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {sessions.map((session) => (
                <option key={session.session_id} value={session.session_id}>
                  {session.date} ({session.video_count} videos)
                </option>
              ))}
            </Select>
          </div>

          <div className="space-y-2">
            <Button
              onClick={() => handleDownload(false)}
              className="w-full"
              disabled={!selectedSession || isDownloading}
            >
              {isDownloading ? 'Downloading...' : 'Download Selected Session'}
            </Button>

            <Button
              onClick={() => handleDownload(true)}
              variant="secondary"
              className="w-full"
              disabled={isDownloading}
            >
              {isDownloading ? 'Downloading...' : 'Download All Sessions'}
            </Button>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}