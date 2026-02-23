'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { authApi } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/client';
import { useAuth } from '@/lib/contexts/auth-context';
import { changePasswordSchema } from '@/lib/validation/password';
import { z } from 'zod';

export default function ChangePasswordPage() {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<{ newPassword?: string; confirmPassword?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { refreshAuthStatus } = useAuth();

  const isFormValid = newPassword.length > 0 && confirmPassword.length > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      changePasswordSchema.parse({ newPassword, confirmPassword });
    } catch (err) {
      if (err instanceof z.ZodError) {
        const fieldErrors: { newPassword?: string; confirmPassword?: string } = {};
        err.issues.forEach((issue) => {
          const field = issue.path[0] as 'newPassword' | 'confirmPassword';
          if (!fieldErrors[field]) {
            fieldErrors[field] = issue.message;
          }
        });
        setErrors(fieldErrors);
        return;
      }
    }

    setIsLoading(true);

    try {
      await authApi.changePassword(newPassword, confirmPassword);
      await refreshAuthStatus();
      await new Promise(resolve => setTimeout(resolve, 500));
      router.push('/dashboard');
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.message.toLowerCase().includes('weak') || err.message.toLowerCase().includes('requirement')) {
          setErrors({ newPassword: err.message });
        } else {
          setErrors({ confirmPassword: err.message || 'An error occurred. Please try again.' });
        }
      } else {
        setErrors({ confirmPassword: 'Network error. Please try again.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-6 px-4">
      <div className="text-center">
        <h1 className="text-2xl font-semibold">Change your password</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Set New Password</CardTitle>
        </CardHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="password"
            label="New password"
            placeholder="Enter new password (min. 12 characters)"
            value={newPassword}
            onChange={(e) => {
              setNewPassword(e.target.value);
              setErrors((prev) => ({ ...prev, newPassword: undefined }));
            }}
            error={errors.newPassword}
            disabled={isLoading}
          />

          <Input
            type="password"
            label="Confirm password"
            placeholder="Confirm new password"
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              setErrors((prev) => ({ ...prev, confirmPassword: undefined }));
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
            Change Password
          </Button>
        </form>
      </Card>
    </div>
  );
}