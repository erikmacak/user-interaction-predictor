import { ReactNode } from 'react';

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-full min-h-[100dvh] items-center justify-center overflow-auto bg-slate-50">
      {children}
    </div>
  );
}