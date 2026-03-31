export const APP_CONFIG = {
  NAME: 'User Interaction Predictor',
  SHORT_NAME: 'UIP',
} as const;

export const NAVIGATION_ITEMS = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/agents', label: 'Agents' },
  { href: '/sessions', label: 'Sessions' },
] as const;

export type NavigationItem = (typeof NAVIGATION_ITEMS)[number];