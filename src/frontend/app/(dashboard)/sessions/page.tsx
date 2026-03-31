'use client';

import { useState, useEffect, useCallback } from 'react';
import { format } from 'date-fns';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { EmptyState } from '@/components/layout/empty-state';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { agentsApi, AgentResponse } from '@/lib/api/agents';
import { auditSessionsApi, AuditSessionResponse } from '@/lib/api/audit_sessions';

const PAGE_TEXT = {
  HEADING: 'Sessions',
  DESCRIPTION: 'Manage audit sessions and monitoring',
  INSTRUCTION: 'Once the session starts, copy the Session ID and assign it to the agent',
  CARD_TITLE: 'Start New Session',
  CARD_DESCRIPTION: 'Select an offline agent to begin an audit session',
  SELECT_LABEL: 'Select Agent',
  LOADING_AGENTS: 'Loading agents...',
  NO_AGENTS: 'No offline agents available',
  CHOOSE_AGENT: 'Choose an agent...',
  BUTTON_STARTING: 'Starting...',
  BUTTON_START: 'Start Session',
  DIVIDER_TEXT: 'Active Sessions',
  RUNNING_TITLE: 'Running Sessions',
  LOADING_SESSIONS: 'Loading sessions...',
  NO_SESSIONS: 'No active sessions',
  NO_SESSIONS_HINT: 'Start a session to begin auditing',
  BADGE_RUNNING: 'Running',
  BUTTON_COPY: 'Copy Session ID',
  BUTTON_COPIED: 'Copied!',
  BUTTON_STOP: 'Stop Session',
  BUTTON_STOP_MOBILE: 'Stop',
  STATUS_OPERATING: 'Operating',
  EMPTY_TITLE: 'Loading system overview',
  EMPTY_DESCRIPTION: 'Please wait while we load system configuration',
} as const;

const COPY_TIMEOUT = 2000;

const TIME_FORMAT = 'HH:mm';
const TIMEZONE_OFFSET_HOURS = 1;

const STYLES = {
  DIVIDER_CONTAINER: 'relative mb-6',
  DIVIDER_LINE: 'h-px bg-slate-300',
  DIVIDER_TEXT: 'absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-50 px-3 text-xs font-medium text-slate-500',
  SESSION_ITEM: 'p-4 transition-colors hover:bg-slate-50',
  SESSION_DESKTOP: 'hidden md:block',
  SESSION_MOBILE: 'md:hidden',
  SESSION_HEADER: 'mb-2 flex items-start justify-between',
  SESSION_NAME: 'font-medium text-slate-900',
  SESSION_BADGE: 'inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700',
  SESSION_INFO: 'mb-2 text-xs text-slate-600',
  SESSION_INFO_MOBILE: 'mb-3 text-xs text-slate-600',
  SESSION_ACTIONS: 'flex items-center gap-2',
  SESSION_ACTIONS_MOBILE: 'flex gap-2',
  EMPTY_CONTAINER: 'flex items-center justify-center p-8 text-center',
  EMPTY_TITLE: 'text-sm font-medium text-slate-900',
  EMPTY_HINT: 'mt-1 text-xs text-slate-600',
} as const;

function formatStartTime(dateString: string): string {
  const date = new Date(dateString);
  date.setHours(date.getHours() + TIMEZONE_OFFSET_HOURS);
  return format(date, TIME_FORMAT);
}

export default function SessionsPage() {
  const [agents, setAgents] = useState<AgentResponse[]>([]);
  const [runningSessions, setRunningSessions] = useState<AuditSessionResponse[]>([]);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingAgents, setIsLoadingAgents] = useState(true);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedSessionId, setCopiedSessionId] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    setIsLoadingAgents(true);
    try {
      const data = await agentsApi.list('offline');
      setAgents(data.agents);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoadingAgents(false);
    }
  }, []);

  const fetchRunningSessions = useCallback(async () => {
    setIsLoadingSessions(true);
    try {
      const data = await auditSessionsApi.listRunning();
      setRunningSessions(data.sessions);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoadingSessions(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
    fetchRunningSessions();
    setIsLoading(false);
  }, [fetchAgents, fetchRunningSessions]);

  const isFormValid = selectedAgent.length > 0;

  const handleStartSession = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedAgent) return;

    setIsStarting(true);
    setError(null);

    try {
      await auditSessionsApi.start(selectedAgent);
      await Promise.all([fetchAgents(), fetchRunningSessions()]);
      setSelectedAgent('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsStarting(false);
    }
  };

  const handleEndSession = async (sessionId: string) => {
    try {
      await auditSessionsApi.stop(sessionId);
      await Promise.all([fetchAgents(), fetchRunningSessions()]);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCopySessionId = async (sessionId: string) => {
    try {
      await navigator.clipboard.writeText(sessionId);
      setCopiedSessionId(sessionId);
      setTimeout(() => setCopiedSessionId(null), COPY_TIMEOUT);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const getSelectPlaceholder = (): string => {
    if (isLoadingAgents) return PAGE_TEXT.LOADING_AGENTS;
    if (agents.length === 0) return PAGE_TEXT.NO_AGENTS;
    return PAGE_TEXT.CHOOSE_AGENT;
  };

  const getSessionsDescription = (): string => {
    if (isLoadingSessions) return PAGE_TEXT.LOADING_SESSIONS;
    if (runningSessions.length === 0) return PAGE_TEXT.NO_SESSIONS;
    return `${runningSessions.length} active session(s)`;
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <EmptyState
          title={PAGE_TEXT.EMPTY_TITLE}
          description={PAGE_TEXT.EMPTY_DESCRIPTION}
        />
      </div>
    );
  }

  if (error && agents.length === 0 && runningSessions.length === 0) {
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
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">{PAGE_TEXT.HEADING}</h1>
        <p className="mt-1 text-sm text-slate-600">{PAGE_TEXT.DESCRIPTION}</p>
        <p className="mt-4 text-sm text-slate-600">{PAGE_TEXT.INSTRUCTION}</p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">{PAGE_TEXT.CARD_TITLE}</CardTitle>
          <CardDescription className="text-xs">
            {PAGE_TEXT.CARD_DESCRIPTION}
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleStartSession} className="space-y-3">
          <Select
            label={PAGE_TEXT.SELECT_LABEL}
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            disabled={isLoadingAgents || isStarting}
          >
            <option value="" disabled>
              {getSelectPlaceholder()}
            </option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} ({agent.platform})
              </option>
            ))}
          </Select>

          <Button
            type="submit"
            className="w-full"
            disabled={!isFormValid || isStarting || isLoadingAgents}
          >
            {isStarting ? PAGE_TEXT.BUTTON_STARTING : PAGE_TEXT.BUTTON_START}
          </Button>
        </form>
      </Card>

      <div className={STYLES.DIVIDER_CONTAINER}>
        <div className={STYLES.DIVIDER_LINE} />
        <span className={STYLES.DIVIDER_TEXT}>{PAGE_TEXT.DIVIDER_TEXT}</span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{PAGE_TEXT.RUNNING_TITLE}</CardTitle>
          <CardDescription className="text-xs">
            {getSessionsDescription()}
          </CardDescription>
        </CardHeader>

        <div className="border-t border-slate-200">
          {isLoadingSessions ? (
            <div className={STYLES.EMPTY_CONTAINER}>
              <div>
                <p className={STYLES.EMPTY_TITLE}>{PAGE_TEXT.LOADING_SESSIONS}</p>
              </div>
            </div>
          ) : runningSessions.length === 0 ? (
            <div className={STYLES.EMPTY_CONTAINER}>
              <div>
                <p className={STYLES.EMPTY_TITLE}>{PAGE_TEXT.NO_SESSIONS}</p>
                <p className={STYLES.EMPTY_HINT}>{PAGE_TEXT.NO_SESSIONS_HINT}</p>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-slate-200">
              {runningSessions.map((session) => (
                <div key={session.id} className={STYLES.SESSION_ITEM}>
                  <div className={STYLES.SESSION_DESKTOP}>
                    <div className={STYLES.SESSION_HEADER}>
                      <p className={STYLES.SESSION_NAME}>{session.agent_name}</p>
                      <span className={STYLES.SESSION_BADGE}>
                        {PAGE_TEXT.BADGE_RUNNING}
                      </span>
                    </div>

                    <p className={STYLES.SESSION_INFO}>
                      {session.agent_platform} • Started at{' '}
                      {formatStartTime(session.started_at)}
                    </p>

                    <div className={STYLES.SESSION_ACTIONS}>
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => handleCopySessionId(session.id)}
                        className="h-8 px-3 text-xs"
                      >
                        {copiedSessionId === session.id
                          ? PAGE_TEXT.BUTTON_COPIED
                          : PAGE_TEXT.BUTTON_COPY}
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => handleEndSession(session.id)}
                        className="h-8 px-3 text-xs"
                      >
                        {PAGE_TEXT.BUTTON_STOP}
                      </Button>
                    </div>
                  </div>

                  <div className={STYLES.SESSION_MOBILE}>
                    <div className={STYLES.SESSION_HEADER}>
                      <p className={STYLES.SESSION_NAME}>{session.agent_name}</p>
                      <span className={STYLES.SESSION_BADGE}>
                        {PAGE_TEXT.BADGE_RUNNING}
                      </span>
                    </div>

                    <p className={STYLES.SESSION_INFO_MOBILE}>
                      {session.agent_platform} • Started at{' '}
                      {formatStartTime(session.started_at)}
                    </p>

                    <div className={STYLES.SESSION_ACTIONS_MOBILE}>
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => handleCopySessionId(session.id)}
                        className="flex-1 text-xs"
                      >
                        {copiedSessionId === session.id
                          ? PAGE_TEXT.BUTTON_COPIED
                          : PAGE_TEXT.BUTTON_COPY}
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => handleEndSession(session.id)}
                        className="flex-1 text-xs"
                      >
                        {PAGE_TEXT.BUTTON_STOP_MOBILE}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}