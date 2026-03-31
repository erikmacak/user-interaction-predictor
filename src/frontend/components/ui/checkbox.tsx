import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils/cn';

const CHECKBOX_STYLES = {
  INPUT: [
    'h-4 w-4 rounded border-slate-300 text-slate-900',
    'focus:ring-2 focus:ring-slate-500 focus:ring-offset-2',
    'disabled:cursor-not-allowed disabled:opacity-50',
  ].join(' '),
  CONTAINER: 'flex items-center gap-2',
  LABEL: 'text-sm font-medium text-slate-700',
} as const;

export interface CheckboxProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

function generateCheckboxId(id?: string, label?: string): string | undefined {
  return id || label?.toLowerCase().replace(/\s+/g, '-');
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, id, ...props }, ref) => {
    const checkboxId = generateCheckboxId(id, label);

    return (
      <div className={CHECKBOX_STYLES.CONTAINER}>
        <input
          id={checkboxId}
          type="checkbox"
          ref={ref}
          className={cn(CHECKBOX_STYLES.INPUT, className)}
          {...props}
        />
        {label && (
          <label htmlFor={checkboxId} className={CHECKBOX_STYLES.LABEL}>
            {label}
          </label>
        )}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';