import { ReactNode } from 'react';
import { cn } from '@/lib/utils/cn';

const DIALOG_STYLES = {
  OVERLAY: 'fixed inset-0 bg-black/50',
  CONTAINER: 'fixed inset-0 z-50 flex items-center justify-center p-4',
  CONTENT_WRAPPER: 'relative z-50 w-full',
  CONTENT: 'mx-auto w-full max-w-md rounded-lg bg-white p-6 shadow-lg',
  HEADER: 'mb-4',
  TITLE: 'text-lg font-semibold text-slate-900',
  DESCRIPTION: 'mt-2 text-sm text-slate-600',
  FOOTER: 'mt-6 flex justify-end gap-2',
} as const;

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: ReactNode;
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  if (!open) return null;

  return (
    <div className={DIALOG_STYLES.CONTAINER}>
      <div
        className={DIALOG_STYLES.OVERLAY}
        onClick={() => onOpenChange(false)}
      />
      <div className={DIALOG_STYLES.CONTENT_WRAPPER}>{children}</div>
    </div>
  );
}

interface DialogContentProps {
  children: ReactNode;
  className?: string;
}

export function DialogContent({ children, className }: DialogContentProps) {
  return (
    <div className={cn(DIALOG_STYLES.CONTENT, className)}>
      {children}
    </div>
  );
}

interface DialogHeaderProps {
  children: ReactNode;
}

export function DialogHeader({ children }: DialogHeaderProps) {
  return <div className={DIALOG_STYLES.HEADER}>{children}</div>;
}

interface DialogTitleProps {
  children: ReactNode;
}

export function DialogTitle({ children }: DialogTitleProps) {
  return <h2 className={DIALOG_STYLES.TITLE}>{children}</h2>;
}

interface DialogDescriptionProps {
  children: ReactNode;
}

export function DialogDescription({ children }: DialogDescriptionProps) {
  return <p className={DIALOG_STYLES.DESCRIPTION}>{children}</p>;
}

interface DialogFooterProps {
  children: ReactNode;
}

export function DialogFooter({ children }: DialogFooterProps) {
  return <div className={DIALOG_STYLES.FOOTER}>{children}</div>;
}