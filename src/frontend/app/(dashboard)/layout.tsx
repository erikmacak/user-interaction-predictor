'use client';

import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { Sidebar } from '@/components/layout/sidebar';
import { Shell } from '@/components/layout/shell';
import { AuthGate } from '@/components/layout/auth-gate';

interface DashboardLayoutProps {
  children: ReactNode;
}

const CENTERED_ROUTES = {
  PATTERNS: ['/agents/', '/edit', '/audit-data', '/new'],
} as const;

function shouldCenterContent(pathname: string): boolean {
  const hasAgentsPath = pathname.includes(CENTERED_ROUTES.PATTERNS[0]);
  const hasEditPath = pathname.includes(CENTERED_ROUTES.PATTERNS[1]);
  const hasAuditDataPath = pathname.includes(CENTERED_ROUTES.PATTERNS[2]);
  const hasNewPath = pathname.includes(CENTERED_ROUTES.PATTERNS[3]);

  return hasAgentsPath && (hasEditPath || hasAuditDataPath || hasNewPath);
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname();
  const isCentered = shouldCenterContent(pathname);

  return (
    <AuthGate>
      <div className="flex h-[100dvh] overflow-hidden">
        <Sidebar />
        <Shell centered={isCentered}>{children}</Shell>
      </div>
    </AuthGate>
  );
}