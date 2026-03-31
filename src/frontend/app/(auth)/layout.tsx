import { ReactNode } from 'react';

const AUTH_LAYOUT_STYLES = [
  'flex h-full min-h-[100dvh] items-center justify-center',
  'overflow-auto bg-slate-50',
].join(' ');

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return <div className={AUTH_LAYOUT_STYLES}>{children}</div>;
}