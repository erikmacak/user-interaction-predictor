'use client';

import { ReactNode } from 'react';

interface AuthGateProps {
  children: ReactNode;
}

export function AuthGate({ children }: AuthGateProps) {
  const isAuthenticated = true;

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}