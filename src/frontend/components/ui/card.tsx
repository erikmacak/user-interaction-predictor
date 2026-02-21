import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils/cn';

export const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'rounded-lg border border-slate-200 bg-white p-6 shadow-sm',
        className
      )}
      {...props}
    />
  )
);

Card.displayName = 'Card';

export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
  <div ref={ref} className={cn('mb-4', className)} {...props} />
));

CardHeader.displayName = 'CardHeader';

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('text-lg font-semibold text-slate-900', className)}
    {...props}
  />
));

CardTitle.displayName = 'CardTitle';

export const CardDescription = forwardRef<HTMLParagraphElement,HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-slate-600', className)}
    {...props}
  />
));

CardDescription.displayName = 'CardDescription';