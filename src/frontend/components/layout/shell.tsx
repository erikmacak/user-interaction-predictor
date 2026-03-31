import { ReactNode } from 'react';
import { cn } from '@/lib/utils/cn';

interface ShellProps {
  children: ReactNode;
  centered?: boolean;
}

const SHELL_STYLES = {
  BASE: 'relative flex-1 overflow-y-auto p-6 pt-20 md:p-10 md:pt-10 h-full',
  CENTERED: 'flex flex-col items-center justify-center',
} as const;

export function Shell({ children, centered = false }: ShellProps) {
  return (
    <main className={cn(SHELL_STYLES.BASE, centered && SHELL_STYLES.CENTERED)}>
      {children}
    </main>
  );
}