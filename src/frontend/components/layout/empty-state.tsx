import { ReactNode } from 'react';

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

const EMPTY_STATE_STYLES = {
  CONTAINER: 'text-center',
  TITLE: 'text-lg font-medium text-slate-900',
  DESCRIPTION: 'mt-1 text-sm text-slate-600',
  ACTION: 'mt-6',
} as const;

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className={EMPTY_STATE_STYLES.CONTAINER}>
      <h2 className={EMPTY_STATE_STYLES.TITLE}>{title}</h2>
      {description && (
        <p className={EMPTY_STATE_STYLES.DESCRIPTION}>{description}</p>
      )}
      {action && <div className={EMPTY_STATE_STYLES.ACTION}>{action}</div>}
    </div>
  );
}