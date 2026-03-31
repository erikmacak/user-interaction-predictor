import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils/cn';

const CARD_STYLES = {
  BASE: 'rounded-lg border border-slate-200 bg-white p-6 shadow-sm',
  HEADER: 'mb-4',
  TITLE: 'text-lg font-semibold text-slate-900',
  DESCRIPTION: 'text-sm text-slate-600',
} as const;

export const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(CARD_STYLES.BASE, className)}
      {...props}
    />
  )
);

Card.displayName = 'Card';

export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn(CARD_STYLES.HEADER, className)} {...props} />
  )
);

CardHeader.displayName = 'CardHeader';

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(CARD_STYLES.TITLE, className)}
    {...props}
  />
));

CardTitle.displayName = 'CardTitle';

export const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn(CARD_STYLES.DESCRIPTION, className)}
    {...props}
  />
));

CardDescription.displayName = 'CardDescription';