'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { APP_CONFIG } from '@/constants';
import { authApi } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/client';
import { useAuth } from '@/lib/contexts/auth-context';

const PAGE_TEXT = {
  CARD_TITLE: 'Admin Panel Access',
  PASSWORD_PLACEHOLDER: 'Password',
  SUBMIT_BUTTON: 'Enter',
  ERROR_REQUIRED: 'Password is required',
  ERROR_INVALID: 'Invalid password',
  ERROR_ALREADY_AUTH: 'Already authenticated. Please logout first.',
  ERROR_NETWORK: 'Network error. Please check your connection.',
  ERROR_DEFAULT: 'An error occurred. Please try again.',
} as const;

const ROUTES = {
  DASHBOARD: '/dashboard',
  CHANGE_PASSWORD: '/change-password',
} as const;

const HTTP_STATUS = {
  UNAUTHORIZED: 401,
  CONFLICT: 409,
} as const;

export default function LoginPage() {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { setAuthState, isAuthenticated, mustChangePassword } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      const route = mustChangePassword
        ? ROUTES.CHANGE_PASSWORD
        : ROUTES.DASHBOARD;
      router.push(route);
    }
  }, [isAuthenticated, mustChangePassword, router]);

  const clearError = useCallback(() => setError(''), []);

  const getErrorMessage = useCallback((err: unknown): string => {
    if (err instanceof ApiError) {
      if (err.status === HTTP_STATUS.UNAUTHORIZED) {
        return PAGE_TEXT.ERROR_INVALID;
      }
      if (err.status === HTTP_STATUS.CONFLICT) {
        return PAGE_TEXT.ERROR_ALREADY_AUTH;
      }
      return err.message || PAGE_TEXT.ERROR_DEFAULT;
    }
    return PAGE_TEXT.ERROR_NETWORK;
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!password) {
      setError(PAGE_TEXT.ERROR_REQUIRED);
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await authApi.login(password);

      setAuthState(true, response.must_change_password);

      const route = response.must_change_password
        ? ROUTES.CHANGE_PASSWORD
        : ROUTES.DASHBOARD;
      router.push(route);
    } catch (err) {
      setError(getErrorMessage(err));
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
        <h1 className="text-2xl font-semibold">{APP_CONFIG.NAME}</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{PAGE_TEXT.CARD_TITLE}</CardTitle>
        </CardHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="password"
            placeholder={PAGE_TEXT.PASSWORD_PLACEHOLDER}
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              clearError();
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
            {PAGE_TEXT.SUBMIT_BUTTON}
          </Button>
        </form>
      </Card>
    </div>
  );
}