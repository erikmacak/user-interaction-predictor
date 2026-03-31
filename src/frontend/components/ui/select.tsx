import { SelectHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils/cn';

const SELECT_STYLES = {
  WRAPPER: 'w-full',
  LABEL: 'mb-1.5 block text-sm font-medium text-slate-700',
  SELECT: [
    'flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-500 focus-visible:ring-offset-2',
    'disabled:cursor-not-allowed disabled:opacity-50',
  ].join(' '),
  SELECT_ERROR: 'border-red-500 focus-visible:ring-red-500',
  ERROR_MESSAGE: 'mt-1.5 text-sm text-red-600',
} as const;

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

function generateSelectId(id?: string, label?: string): string | undefined {
  return id || label?.toLowerCase().replace(/\s+/g, '-');
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, id, children, ...props }, ref) => {
    const selectId = generateSelectId(id, label);

    return (
      <div className={SELECT_STYLES.WRAPPER}>
        {label && (
          <label htmlFor={selectId} className={SELECT_STYLES.LABEL}>
            {label}
          </label>
        )}
        <select
          id={selectId}
          ref={ref}
          className={cn(
            SELECT_STYLES.SELECT,
            error && SELECT_STYLES.SELECT_ERROR,
            className
          )}
          {...props}
        >
          {children}
        </select>
        {error && (
          <p className={SELECT_STYLES.ERROR_MESSAGE} role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';