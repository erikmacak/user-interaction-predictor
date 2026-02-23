'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { APP_NAME } from '@/constants';
import { authApi } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/client';
import { useAuth } from '@/lib/contexts/auth-context';

export default function LoginPage() {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { setAuthState, isAuthenticated, mustChangePassword } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      if (mustChangePassword) {
        router.push('/change-password');
      } else {
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, mustChangePassword, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!password) {
      setError('Password is required');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await authApi.login(password);
      
      setAuthState(true, response.must_change_password);
      
      if (response.must_change_password) {
        router.push('/change-password');
      } else {
        router.push('/dashboard');
      }
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError('Invalid password');
        } else if (err.status === 409) {
          setError('Already authenticated. Please logout first.');
        } else {
          setError(err.message || 'An error occurred. Please try again.');
        }
      } else {
        setError('Network error. Please check your connection.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isAuthenticated) {
    return null;
  }

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
            disabled={isLoading}
          />

          <Button 
            type="submit" 
            className="w-full" 
            isLoading={isLoading}
            disabled={!password || isLoading}
          >
            Enter
          </Button>
        </form>
      </Card>
    </div>
  );
}