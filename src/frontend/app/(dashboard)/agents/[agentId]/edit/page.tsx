'use client';

import { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import { MOCK_AGENTS } from '@/lib/mock-data';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { PLATFORMS, PREDICTOR_VERSIONS } from '@/constants';
import { Platform, AgentState } from '@/types';

interface PageProps {
  params: Promise<{ agentId: string }>;
}

export default function EditAgentPage({ params }: PageProps) {
  const router = useRouter();
  const { agentId } = use(params);
  const agent = MOCK_AGENTS.find((a) => a.id === agentId);

  const [formData, setFormData] = useState({
    name: agent?.name || '',
    platform: (agent?.platform || 'YouTube') as Platform,
    predictorVersion: agent?.predictorVersion || 'v1',
    state: (agent?.state || 'offline') as AgentState,
    checkVideoExistence: agent?.checkVideoExistence ?? true,
  });
  const [stateFile, setStateFile] = useState<File | null>(null);

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.push('/agents');
  };

  if (!agent) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-medium text-slate-900">
            Agent not found
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            The agent you're looking for doesn't exist.
          </p>
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
            {PLATFORMS.map((platform) => (
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
            {PREDICTOR_VERSIONS.map((version) => (
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
            <option value="auditing">Auditing</option>
            <option value="offline">Offline</option>
            <option value="banned">Banned</option>
          </Select>

          <Checkbox
            label="Check video existence"
            checked={formData.checkVideoExistence}
            onChange={(e) =>
              setFormData({
                ...formData,
                checkVideoExistence: e.target.checked,
              })
            }
          />

          <div className="flex gap-2 pt-1 md:pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.back()}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" className="flex-1" disabled={!isFormValid}>
              Save Changes
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}