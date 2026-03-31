import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils/cn';

const INPUT_STYLES = {
  WRAPPER: 'w-full',
  LABEL: 'mb-1.5 block text-sm font-medium text-slate-700',
  INPUT: [
    'flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm',
    'placeholder:text-slate-400',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-500 focus-visible:ring-offset-2',
    'disabled:cursor-not-allowed disabled:opacity-50',
  ].join(' '),
  INPUT_ERROR: 'border-red-500 focus-visible:ring-red-500',
  ERROR_MESSAGE: 'mt-1.5 text-sm text-red-600',
} as const;

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
}

function generateInputId(id?: string, label?: string): string | undefined {
  return id || label?.toLowerCase().replace(/\s+/g, '-');
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, label, id, type = 'text', ...props }, ref) => {
    const inputId = generateInputId(id, label);

    return (
      <div className={INPUT_STYLES.WRAPPER}>
        {label && (
          <label htmlFor={inputId} className={INPUT_STYLES.LABEL}>
            {label}
          </label>
        )}
        <input
          id={inputId}
          type={type}
          ref={ref}
          className={cn(
            INPUT_STYLES.INPUT,
            error && INPUT_STYLES.INPUT_ERROR,
            className
          )}
          {...props}
        />
        {error && (
          <p className={INPUT_STYLES.ERROR_MESSAGE} role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';