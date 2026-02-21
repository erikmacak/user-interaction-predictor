import { Platform } from '@/types';

export const APP_NAME = 'User Interaction Predictor';
export const APP_SHORT_NAME = 'UIP';

export const PLATFORMS: Platform[] = ['YouTube', 'TikTok', 'Instagram'];
export const PREDICTOR_VERSIONS = ['v1', 'v2', 'v3'];

export const NAVIGATION_ITEMS = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/agents', label: 'Agents' },
  { href: '/sessions', label: 'Sessions' },
] as const;