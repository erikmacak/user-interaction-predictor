'use client';

import { ReactNode } from 'react';
import { useAuth } from '@/lib/contexts/auth-context';

interface AuthGateProps {
  children: ReactNode;
}

const SPINNER_STYLES = [
  'h-8 w-8 animate-spin rounded-full',
  'border-4 border-slate-300 border-t-slate-900',
].join(' ');

const LOADING_CONTAINER_STYLES = 'flex h-full items-center justify-center';

export function AuthGate({ children }: AuthGateProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className={LOADING_CONTAINER_STYLES}>
        <div className={SPINNER_STYLES} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}