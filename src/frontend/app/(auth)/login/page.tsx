'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { APP_NAME } from '@/constants';

export default function LoginPage() {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!password) {
      setError('Password is required');
    } else {
      setError('Invalid password');
    }
  };

  return (
    <div className="w-full max-w-md space-y-6 px-4">
      <div className="text-center">
        <h1 className="text-2xl font-semibold">{APP_NAME}</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Admin Panel Access</CardTitle>
        </CardHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setError('');
            }}
            error={error}
          />

          <Button type="submit" className="w-full">
            Enter
          </Button>
        </form>
      </Card>
    </div>
  );
}