'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { NAVIGATION_ITEMS, APP_SHORT_NAME } from '@/constants';
import { cn } from '@/lib/utils/cn';
import { useAuth } from '@/lib/contexts/auth-context';

export function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const { logout } = useAuth();

  const handleLogout = async () => {
    setIsOpen(false);
    await logout();
  };

  const NavLinks = () => (
    <nav className="space-y-1">
      {NAVIGATION_ITEMS.map((item) => {
        const isActive = pathname.startsWith(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={() => setIsOpen(false)}
            className={cn(
              'block rounded-md px-3 py-2 text-sm font-medium transition-colors',
              isActive
                ? 'bg-slate-800 text-white'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
            )}
          >
            {item.label}
          </Link>
        );
      })}
      <button
        onClick={handleLogout}
        className="block w-full rounded-md px-3 py-2 text-left text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800 hover:text-white"
      >
        Logout
      </button>
    </nav>
  );

  return (
    <>
      <aside className="hidden w-64 border-r border-slate-200 bg-slate-900 p-6 md:block">
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-white">
            {APP_SHORT_NAME} Panel
          </h2>
        </div>
        <NavLinks />
      </aside>

      <div className="fixed left-0 right-0 top-0 z-40 flex h-14 items-center border-b border-slate-200 bg-slate-900 px-4 md:hidden">
        <button
          onClick={() => setIsOpen(true)}
          className="text-2xl leading-none text-white"
          aria-label="Open menu"
        >
          ☰
        </button>
        <span className="ml-4 font-semibold text-white">
          {APP_SHORT_NAME} Panel
        </span>
      </div>

      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-full w-64 bg-slate-900 p-6 transition-transform md:hidden',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-white">
            {APP_SHORT_NAME} Panel
          </h2>
        </div>
        <NavLinks />
      </aside>
    </>
  );
}