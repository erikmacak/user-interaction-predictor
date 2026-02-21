'use client';
import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { Sidebar } from '@/components/layout/sidebar';
import { Shell } from '@/components/layout/shell';
import { AuthGate } from '@/components/layout/auth-gate';

export default function DashboardLayout({
  children,
}: {
  children: ReactNode;
}) {
  const pathname = usePathname();

  const isCentered =
    pathname.includes('/agents/') &&
    (pathname.includes('/edit') ||
      pathname.includes('/audit-data') ||
      pathname.includes('/new'));

  return (
    <AuthGate>
      <div className="flex h-[100dvh] overflow-hidden">
        <Sidebar />
        <Shell centered={isCentered}>{children}</Shell>
      </div>
    </AuthGate>
  );
}