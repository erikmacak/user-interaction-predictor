import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { APP_CONFIG } from '@/constants';
import { AuthProvider } from '@/lib/contexts/auth-context';

const inter = Inter({ subsets: ['latin'] });

const APP_METADATA: Metadata = {
  title: APP_CONFIG.NAME,
  description: 'Social media AI algorithms auditing system',
};

export const metadata = APP_METADATA;

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className="h-full" suppressHydrationWarning>
      <body className={`${inter.className} h-full overflow-hidden`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}