'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { z } from 'zod';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { authApi } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/client';
import { useAuth } from '@/lib/contexts/auth-context';
import { changePasswordSchema } from '@/lib/validation/password';

const PAGE_TEXT = {
  HEADING: 'Change your password',
  CARD_TITLE: 'Set New Password',
  NEW_PASSWORD_LABEL: 'New password',
  NEW_PASSWORD_PLACEHOLDER: 'Enter new password (min. 12 characters)',
  CONFIRM_PASSWORD_LABEL: 'Confirm password',
  CONFIRM_PASSWORD_PLACEHOLDER: 'Confirm new password',
  SUBMIT_BUTTON: 'Change Password',
} as const;

const ROUTES = {
  DASHBOARD: '/dashboard',
} as const;

const REDIRECT_DELAY = 500;

interface FormErrors {
  newPassword?: string;
  confirmPassword?: string;
}

export default function ChangePasswordPage() {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { refreshAuthStatus } = useAuth();

  const isFormValid = newPassword.length > 0 && confirmPassword.length > 0;

  const clearFieldError = useCallback((field: keyof FormErrors) => {
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  }, []);

  const handleValidationError = useCallback((err: z.ZodError) => {
    const fieldErrors: FormErrors = {};
    err.issues.forEach((issue) => {
      const field = issue.path[0] as keyof FormErrors;
      if (!fieldErrors[field]) {
        fieldErrors[field] = issue.message;
      }
    });
    setErrors(fieldErrors);
  }, []);

  const handleApiError = useCallback((err: unknown) => {
    if (err instanceof ApiError) {
      const message = err.message.toLowerCase();
      const isPasswordError =
        message.includes('weak') || message.includes('requirement');

      if (isPasswordError) {
        setErrors({ newPassword: err.message });
      } else {
        setErrors({
          confirmPassword: err.message || 'An error occurred. Please try again.',
        });
      }
    } else {
      setErrors({ confirmPassword: 'Network error. Please try again.' });
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      changePasswordSchema.parse({ newPassword, confirmPassword });
    } catch (err) {
      if (err instanceof z.ZodError) {
        handleValidationError(err);
      }
      return;
    }

    setIsLoading(true);

    try {
      await authApi.changePassword(newPassword, confirmPassword);
      await refreshAuthStatus();
      await new Promise((resolve) => setTimeout(resolve, REDIRECT_DELAY));
      router.push(ROUTES.DASHBOARD);
    } catch (err) {
      handleApiError(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-6 px-4">
      <div className="text-center">
        <h1 className="text-2xl font-semibold">{PAGE_TEXT.HEADING}</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{PAGE_TEXT.CARD_TITLE}</CardTitle>
        </CardHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="password"
            label={PAGE_TEXT.NEW_PASSWORD_LABEL}
            placeholder={PAGE_TEXT.NEW_PASSWORD_PLACEHOLDER}
            value={newPassword}
            onChange={(e) => {
              setNewPassword(e.target.value);
              clearFieldError('newPassword');
            }}
            error={errors.newPassword}
            disabled={isLoading}
          />

          <Input
            type="password"
            label={PAGE_TEXT.CONFIRM_PASSWORD_LABEL}
            placeholder={PAGE_TEXT.CONFIRM_PASSWORD_PLACEHOLDER}
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              clearFieldError('confirmPassword');
            }}
            error={errors.confirmPassword}
            disabled={isLoading}
          />

          <Button
            type="submit"
            className="w-full"
            isLoading={isLoading}
            disabled={!isFormValid || isLoading}
          >
            {PAGE_TEXT.SUBMIT_BUTTON}
          </Button>
        </form>
      </Card>
    </div>
  );
}