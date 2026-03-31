import Link from 'next/link';
import { Button } from '@/components/ui/button';

const NOT_FOUND_STYLES = {
  CONTAINER: 'fixed inset-0 flex flex-col items-center justify-center bg-slate-50 px-4 text-center',
  HEADING: 'mb-2 text-3xl font-semibold',
  DESCRIPTION: 'mb-6 text-slate-600',
} as const;

const NOT_FOUND_TEXT = {
  HEADING: '404',
  DESCRIPTION: 'The page you are looking for does not exist.',
  BUTTON: 'Go to dashboard',
} as const;

const DASHBOARD_ROUTE = '/dashboard';

export default function NotFound() {
  return (
    <div className={NOT_FOUND_STYLES.CONTAINER}>
      <h1 className={NOT_FOUND_STYLES.HEADING}>{NOT_FOUND_TEXT.HEADING}</h1>
      <p className={NOT_FOUND_STYLES.DESCRIPTION}>
        {NOT_FOUND_TEXT.DESCRIPTION}
      </p>
      <Link href={DASHBOARD_ROUTE}>
        <Button>{NOT_FOUND_TEXT.BUTTON}</Button>
      </Link>
    </div>
  );
}