'use client';

import { use, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Platform, AgentState } from '@/types';
import { agentsApi, AgentResponse, AgentUpdateRequest } from '@/lib/api/agents';
import { EmptyState } from '@/components/layout/empty-state';

interface PageProps {
  params: Promise<{ agentId: string }>;
}

const PAGE_TEXT = {
  CARD_TITLE: 'Edit Agent',
  CARD_DESCRIPTION: 'Update agent configuration and settings',
  LABEL_NAME: 'Agent Name',
  LABEL_PLATFORM: 'Platform',
  LABEL_STATE: 'User State Representation',
  LABEL_VERSION: 'Predictor Version',
  LABEL_AGENT_STATE: 'Agent State',
  STATE_DESCRIPTION: 'Upload new JSON file (optional)',
  FILE_ALERT: 'Please upload a valid JSON file',
  BUTTON_REMOVE: 'Remove',
  BUTTON_CANCEL: 'Cancel',
  BUTTON_SAVE: 'Save Changes',
  BUTTON_SAVING: 'Saving...',
  STATE_OFFLINE: 'Offline',
  STATE_BANNED: 'Banned',
  LOADING_TITLE: 'Loading system overview',
  LOADING_DESCRIPTION: 'Please wait while we load system configuration',
} as const;

const ROUTES = {
  AGENTS: '/agents',
} as const;

const FILE_SIZE_DIVISOR = 1024;
const FILE_SIZE_DECIMALS = 1;

const STYLES = {
  FILE_ICON: 'h-4 w-4 text-slate-600',
  FILE_ICON_CONTAINER: 'flex h-8 w-8 items-center justify-center rounded bg-slate-200',
  FILE_NAME: 'text-xs font-medium text-slate-900',
  FILE_SIZE: 'text-xs text-slate-600',
} as const;

const SVG_PATHS = {
  DOCUMENT: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
} as const;

interface FormData {
  name: string;
  platform: Platform;
  predictorVersion: string;
  state: AgentState;
}

function formatFileSize(bytes: number): string {
  return (bytes / FILE_SIZE_DIVISOR).toFixed(FILE_SIZE_DECIMALS);
}

function isValidJsonFile(file: File): boolean {
  return file.type === 'application/json' || file.name.endsWith('.json');
}

export default function EditAgentPage({ params }: PageProps) {
  const router = useRouter();
  const { agentId } = use(params);

  const [agent, setAgent] = useState<AgentResponse | null>(null);
  const [platforms, setPlatforms] = useState<string[]>([]);
  const [predictorVersions, setPredictorVersions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState<FormData>({
    name: '',
    platform: '' as Platform,
    predictorVersion: '',
    state: 'offline',
  });
  const [stateFile, setStateFile] = useState<File | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [agentData, platformsList, versions] = await Promise.all([
        agentsApi.get(agentId),
        agentsApi.getPlatforms(),
        agentsApi.getVersions(),
      ]);

      setAgent(agentData);
      setPlatforms(platformsList);
      setPredictorVersions(versions);
      setFormData({
        name: agentData.name,
        platform: agentData.platform,
        predictorVersion: agentData.predictor_version,
        state: agentData.state,
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [agentId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const isFormValid = formData.name.trim().length > 0;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (isValidJsonFile(file)) {
      setStateFile(file);
    } else {
      alert(PAGE_TEXT.FILE_ALERT);
      e.target.value = '';
    }
  };

  const handleRemoveFile = useCallback(() => {
    setStateFile(null);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsSubmitting(true);
    setError(null);

    try {
      const updateData: AgentUpdateRequest = {
        name: formData.name,
        platform: formData.platform,
        predictor_version: formData.predictorVersion,
        state: formData.state,
      };

      if (stateFile) {
        const fileContent = await stateFile.text();
        updateData.state_file_data = fileContent;
      }

      await agentsApi.update(agentId, updateData);
      router.push(ROUTES.AGENTS);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
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
    <div className="mx-auto w-full max-w-xl px-4 md:max-w-3xl md:px-0">
      <Card className="p-3 md:p-4">
        <CardHeader className="mb-2 p-0 md:mb-3">
          <CardTitle className="text-base md:text-lg">
            {PAGE_TEXT.CARD_TITLE}
          </CardTitle>
          <CardDescription className="text-xs">
            {PAGE_TEXT.CARD_DESCRIPTION}
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit} className="space-y-2 md:space-y-3">
          <Input
            label={PAGE_TEXT.LABEL_NAME}
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <Select
            label={PAGE_TEXT.LABEL_PLATFORM}
            value={formData.platform}
            onChange={(e) =>
              setFormData({ ...formData, platform: e.target.value as Platform })
            }
          >
            {platforms.map((platform) => (
              <option key={platform} value={platform}>
                {platform}
              </option>
            ))}
          </Select>

          <div className="space-y-1 md:space-y-1.5">
            <label className="block text-xs font-medium text-slate-700 md:text-sm">
              {PAGE_TEXT.LABEL_STATE}
            </label>
            <div className="rounded-md border border-slate-200 bg-slate-50 p-2 md:p-3">
              {!stateFile ? (
                <div className="space-y-1.5 md:space-y-2">
                  <p className="text-xs text-slate-600">
                    {PAGE_TEXT.STATE_DESCRIPTION}
                  </p>
                  <label className="block">
                    <input
                      type="file"
                      accept=".json,application/json"
                      onChange={handleFileChange}
                      className="block w-full text-xs text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-slate-900 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-white hover:file:bg-slate-800"
                    />
                  </label>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={STYLES.FILE_ICON_CONTAINER}>
                      <svg
                        className={STYLES.FILE_ICON}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d={SVG_PATHS.DOCUMENT}
                        />
                      </svg>
                    </div>
                    <div>
                      <p className={STYLES.FILE_NAME}>{stateFile.name}</p>
                      <p className={STYLES.FILE_SIZE}>
                        {formatFileSize(stateFile.size)} KB
                      </p>
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={handleRemoveFile}
                    className="h-7 px-2 text-xs"
                  >
                    {PAGE_TEXT.BUTTON_REMOVE}
                  </Button>
                </div>
              )}
            </div>
          </div>

          <Select
            label={PAGE_TEXT.LABEL_VERSION}
            value={formData.predictorVersion}
            onChange={(e) =>
              setFormData({ ...formData, predictorVersion: e.target.value })
            }
          >
            {predictorVersions.map((version) => (
              <option key={version} value={version}>
                {version}
              </option>
            ))}
          </Select>

          <Select
            label={PAGE_TEXT.LABEL_AGENT_STATE}
            value={formData.state}
            onChange={(e) =>
              setFormData({ ...formData, state: e.target.value as AgentState })
            }
          >
            <option value="offline">{PAGE_TEXT.STATE_OFFLINE}</option>
            <option value="banned">{PAGE_TEXT.STATE_BANNED}</option>
          </Select>

          <div className="flex gap-2 pt-1 md:pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.back()}
              className="flex-1"
              disabled={isSubmitting}
            >
              {PAGE_TEXT.BUTTON_CANCEL}
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={!isFormValid || isSubmitting}
            >
              {isSubmitting ? PAGE_TEXT.BUTTON_SAVING : PAGE_TEXT.BUTTON_SAVE}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}