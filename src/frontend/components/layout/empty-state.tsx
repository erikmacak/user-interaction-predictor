import { ReactNode } from 'react';

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="text-center">
      <h2 className="text-lg font-medium text-slate-900">{title}</h2>
      {description && (
        <p className="mt-1 text-sm text-slate-600">{description}</p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}