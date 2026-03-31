'use client';

import { use, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { videoLogsApi, SessionData } from '@/lib/api/video_logs';
import { EmptyState } from '@/components/layout/empty-state';
import { agentsApi, AgentResponse } from '@/lib/api/agents';

interface PageProps {
  params: Promise<{ agentId: string }>;
}

const PAGE_TEXT = {
  CARD_TITLE: 'Download Audit Data',
  CARD_DESCRIPTION: 'Download collected audit data for this agent',
  LABEL_SESSION: 'Select Audit Session',
  BUTTON_DOWNLOAD_SESSION: 'Download Selected Session',
  BUTTON_DOWNLOAD_ALL: 'Download All Sessions',
  BUTTON_DOWNLOADING: 'Downloading...',
  LOADING_TITLE: 'Loading system overview',
  LOADING_DESCRIPTION: 'Please wait while we load system configuration',
} as const;

const FILE_NAMES = {
  ALL_DATA: (agentId: string) => `agent_${agentId}_all_data.csv`,
  SESSION_DATA: (date: string) => `session_${date.replace(/-/g, '')}_data.csv`,
  SESSION_DATA_FALLBACK: (sessionId: string) => `session_${sessionId}_data.csv`,
} as const;

function generateSessionLabel(session: SessionData): string {
  return `${session.date} (${session.video_count} videos)`;
}

function triggerFileDownload(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(anchor);
}

export default function AuditDataPage({ params }: PageProps) {
  const router = useRouter();
  const { agentId } = use(params);

  const [agent, setAgent] = useState<AgentResponse | null>(null);
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [selectedSession, setSelectedSession] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [agentData, sessionsData] = await Promise.all([
        agentsApi.get(agentId),
        videoLogsApi.getAgentSessions(agentId),
      ]);

      setAgent(agentData);
      setSessions(sessionsData);

      if (sessionsData.length > 0) {
        setSelectedSession(sessionsData[0].session_id);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [agentId]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const downloadSelectedSession = async () => {
    if (!selectedSession) return;

    const blob = await videoLogsApi.downloadSessionData(agentId, selectedSession);
    const session = sessions.find((s) => s.session_id === selectedSession);
    const filename = session
      ? FILE_NAMES.SESSION_DATA(session.date)
      : FILE_NAMES.SESSION_DATA_FALLBACK(selectedSession);

    triggerFileDownload(blob, filename);
  };

  const downloadAllSessions = async () => {
    const blob = await videoLogsApi.downloadAllData(agentId);
    const filename = FILE_NAMES.ALL_DATA(agentId);
    triggerFileDownload(blob, filename);
  };

  const handleDownload = async (downloadAll: boolean = false) => {
    setIsDownloading(true);

    try {
      if (downloadAll) {
        await downloadAllSessions();
      } else {
        await downloadSelectedSession();
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsDownloading(false);
    }
  };

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
      <div className="mx-auto max-w-2xl">
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <h2 className="text-lg font-medium text-slate-900">
              Error! Something went wrong.
            </h2>
            <p className="mt-1 text-sm text-slate-600">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>{PAGE_TEXT.CARD_TITLE}</CardTitle>
          <CardDescription>{PAGE_TEXT.CARD_DESCRIPTION}</CardDescription>
        </CardHeader>

        <div className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              {PAGE_TEXT.LABEL_SESSION}
            </label>
            <Select
              value={selectedSession}
              onChange={(e) => setSelectedSession(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {sessions.map((session) => (
                <option key={session.session_id} value={session.session_id}>
                  {generateSessionLabel(session)}
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
              {isDownloading
                ? PAGE_TEXT.BUTTON_DOWNLOADING
                : PAGE_TEXT.BUTTON_DOWNLOAD_SESSION}
            </Button>

            <Button
              onClick={() => handleDownload(true)}
              variant="secondary"
              className="w-full"
              disabled={isDownloading}
            >
              {isDownloading
                ? PAGE_TEXT.BUTTON_DOWNLOADING
                : PAGE_TEXT.BUTTON_DOWNLOAD_ALL}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}