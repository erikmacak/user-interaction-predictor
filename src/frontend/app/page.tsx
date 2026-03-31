import { redirect } from 'next/navigation';

const DEFAULT_ROUTE = '/dashboard';

export default function RootPage() {
  redirect(DEFAULT_ROUTE);
}