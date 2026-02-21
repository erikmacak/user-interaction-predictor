'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function ChangePasswordPage() {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  
  const isFormValid = newPassword.length > 0 && confirmPassword.length > 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
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
            placeholder="Enter new password"
            value={newPassword}
            onChange={(e) => {
              setNewPassword(e.target.value);
              setError('');
            }}
          />

          <Input
            type="password"
            label="Confirm password"
            placeholder="Confirm new password"
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              setError('');
            }}
            error={error}
          />

          <Button
            type="submit"
            className="w-full"
            disabled={!isFormValid}
          >
            Change Password
          </Button>
        </form>
      </Card>
    </div>
  );
}