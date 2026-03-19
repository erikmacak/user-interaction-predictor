'use client';

import { use, useState, useEffect } from 'react';
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
import { agentsApi, AgentResponse } from '@/lib/api/agents';
import { EmptyState } from '@/components/layout/empty-state';

interface PageProps {
  params: Promise<{ agentId: string }>;
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
  
  const [formData, setFormData] = useState({
    name: '',
    platform: '' as Platform,
    predictorVersion: 'v1',
    state: 'offline' as AgentState,
  });
  const [stateFile, setStateFile] = useState<File | null>(null);

  useEffect(() => {
    const fetchData = async () => {
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
        setError(err.message || 'Failed to load agent');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [agentId]);

  const isFormValid = formData.name.trim().length > 0;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type === 'application/json' || file.name.endsWith('.json')) {
        setStateFile(file);
      } else {
        alert('Please upload a valid JSON file');
        e.target.value = '';
      }
    }
  };

  const handleRemoveFile = () => {
    setStateFile(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setIsSubmitting(true);
    setError(null);

    try {
      const updateData: any = {
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
      router.push('/agents');
    } catch (err: any) {
      setError(err.message || 'Failed to update agent');
    } finally {
      setIsSubmitting(false);
    }
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

  if (!agent) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-medium text-slate-900">
            Agent not found
          </h2>
          <p className="mt-1 text-sm text-slate-600">{error}</p>
          <Button onClick={() => router.push('/agents')} className="mt-4">
            Back to Agents
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-xl px-4 md:max-w-3xl md:px-0">
      <Card className="p-3 md:p-4">
        <CardHeader className="mb-2 p-0 md:mb-3">
          <CardTitle className="text-base md:text-lg">Edit Agent</CardTitle>
          <CardDescription className="text-xs">
            Update agent configuration and settings
          </CardDescription>
        </CardHeader>

        {error && (
          <div className="mb-3 rounded-md bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-2 md:space-y-3">
          <Input
            label="Agent Name"
            value={formData.name}
            onChange={(e) =>
              setFormData({ ...formData, name: e.target.value })
            }
            required
          />

          <Select
            label="Platform"
            value={formData.platform}
            onChange={(e) =>
              setFormData({
                ...formData,
                platform: e.target.value as Platform,
              })
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
              User State Representation
            </label>
            <div className="rounded-md border border-slate-200 bg-slate-50 p-2 md:p-3">
              {!stateFile ? (
                <div className="space-y-1.5 md:space-y-2">
                  <p className="text-xs text-slate-600">
                    Upload new JSON file (optional)
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
                    <div className="flex h-8 w-8 items-center justify-center rounded bg-slate-200">
                      <svg
                        className="h-4 w-4 text-slate-600"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-900">
                        {stateFile.name}
                      </p>
                      <p className="text-xs text-slate-600">
                        {(stateFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={handleRemoveFile}
                    className="h-7 px-2 text-xs"
                  >
                    Remove
                  </Button>
                </div>
              )}
            </div>
          </div>

          <Select
            label="Predictor Version"
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
            label="Agent State"
            value={formData.state}
            onChange={(e) =>
              setFormData({
                ...formData,
                state: e.target.value as AgentState,
              })
            }
          >
            <option value="offline">Offline</option>
            <option value="banned">Banned</option>
          </Select>

          <div className="flex gap-2 pt-1 md:pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.back()}
              className="flex-1"
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              className="flex-1" 
              disabled={!isFormValid || isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}