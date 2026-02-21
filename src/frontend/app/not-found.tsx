import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function NotFound() {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-slate-50 px-4 text-center">
      <h1 className="mb-2 text-3xl font-semibold">404</h1>
      <p className="mb-6 text-slate-600">
        The page you are looking for does not exist.
      </p>
      <Link href="/dashboard">
        <Button>Go to dashboard</Button>
      </Link>
    </div>
  );
}