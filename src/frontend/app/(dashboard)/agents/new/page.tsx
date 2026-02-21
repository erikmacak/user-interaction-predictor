'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
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
import { Platform } from '@/types';

export default function NewAgentPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    platform: 'YouTube' as Platform,
    predictorVersion: 'v1',
    checkVideoExistence: true,
  });
  const [stateFile, setStateFile] = useState<File | null>(null);

  const isFormValid = formData.name.trim().length > 0 && stateFile !== null;

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

  return (
    <div className="mx-auto w-full max-w-xl px-4 md:max-w-3xl md:px-0"> {/*HERE*/}
      <Card className="p-4">
        <CardHeader className="mb-3 p-0">
          <CardTitle className="text-base md:text-lg">Add New Agent</CardTitle>
          <CardDescription className="text-xs">
            Create a new auditing agent for social media platforms
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit} className="space-y-3">
          <Input
            label="Agent Name"
            placeholder="e.g., agent_youtube_01"
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

          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700">
              User State Representation
            </label>
            <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
              {!stateFile ? (
                <div className="space-y-2">
                  <p className="text-xs text-slate-600">
                    Provide agent information in JSON format
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

          <div className="flex gap-2 pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.back()}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" className="flex-1" disabled={!isFormValid}>
              Create Agent
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}