import { ReactNode } from 'react';

interface ShellProps {
  children: ReactNode;
  centered?: boolean;
}

export function Shell({ children, centered = false }: ShellProps) {
  return (
    <main
      className={`relative flex-1 overflow-y-auto p-6 pt-20 md:p-10 md:pt-10 ${
        centered ? 'flex flex-col items-center justify-center h-full' : 'h-full'
      }`}
    >
      {children}
    </main>
  );
}