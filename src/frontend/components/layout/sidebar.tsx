'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useCallback } from 'react';
import { NAVIGATION_ITEMS, APP_CONFIG } from '@/constants';
import { cn } from '@/lib/utils/cn';
import { useAuth } from '@/lib/contexts/auth-context';

const SIDEBAR_STYLES = {
  DESKTOP: 'hidden w-64 border-r border-slate-200 bg-slate-900 p-6 md:block',
  MOBILE_HEADER: [
    'fixed left-0 right-0 top-0 z-40',
    'flex h-14 items-center',
    'border-b border-slate-200 bg-slate-900 px-4',
    'md:hidden',
  ].join(' '),
  MOBILE_OVERLAY: 'fixed inset-0 z-40 bg-black/40 md:hidden',
  MOBILE_SIDEBAR: [
    'fixed left-0 top-0 z-50 h-full w-64 bg-slate-900 p-6 transition-transform md:hidden',
  ].join(' '),
  HEADER: 'mb-8',
  HEADER_TITLE: 'text-lg font-semibold text-white',
  NAV: 'space-y-1',
  NAV_LINK_BASE: 'block rounded-md px-3 py-2 text-sm font-medium transition-colors',
  NAV_LINK_ACTIVE: 'bg-slate-800 text-white',
  NAV_LINK_INACTIVE: 'text-slate-300 hover:bg-slate-800 hover:text-white',
  LOGOUT_BUTTON: [
    'block w-full rounded-md px-3 py-2 text-left text-sm font-medium',
    'text-slate-300 transition-colors hover:bg-slate-800 hover:text-white',
  ].join(' '),
  MENU_BUTTON: 'text-2xl leading-none text-white',
  MENU_LABEL: 'ml-4 font-semibold text-white',
} as const;

const MENU_ICON = '☰';

export function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const { logout } = useAuth();

  const closeSidebar = useCallback(() => setIsOpen(false), []);
  const openSidebar = useCallback(() => setIsOpen(true), []);

  const handleLogout = useCallback(async () => {
    closeSidebar();
    await logout();
  }, [logout, closeSidebar]);

  const NavLinks = useCallback(() => (
    <nav className={SIDEBAR_STYLES.NAV}>
      {NAVIGATION_ITEMS.map((item) => {
        const isActive = pathname.startsWith(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={closeSidebar}
            className={cn(
              SIDEBAR_STYLES.NAV_LINK_BASE,
              isActive
                ? SIDEBAR_STYLES.NAV_LINK_ACTIVE
                : SIDEBAR_STYLES.NAV_LINK_INACTIVE
            )}
          >
            {item.label}
          </Link>
        );
      })}
      <button onClick={handleLogout} className={SIDEBAR_STYLES.LOGOUT_BUTTON}>
        Logout
      </button>
    </nav>
  ), [pathname, closeSidebar, handleLogout]);

  const SidebarHeader = () => (
    <div className={SIDEBAR_STYLES.HEADER}>
      <h2 className={SIDEBAR_STYLES.HEADER_TITLE}>
        {APP_CONFIG.SHORT_NAME} Panel
      </h2>
    </div>
  );

  return (
    <>
      <aside className={SIDEBAR_STYLES.DESKTOP}>
        <SidebarHeader />
        <NavLinks />
      </aside>

      <div className={SIDEBAR_STYLES.MOBILE_HEADER}>
        <button
          onClick={openSidebar}
          className={SIDEBAR_STYLES.MENU_BUTTON}
          aria-label="Open menu"
        >
          {MENU_ICON}
        </button>
        <span className={SIDEBAR_STYLES.MENU_LABEL}>
          {APP_CONFIG.SHORT_NAME} Panel
        </span>
      </div>

      {isOpen && (
        <div className={SIDEBAR_STYLES.MOBILE_OVERLAY} onClick={closeSidebar} />
      )}

      <aside
        className={cn(
          SIDEBAR_STYLES.MOBILE_SIDEBAR,
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <SidebarHeader />
        <NavLinks />
      </aside>
    </>
  );
}