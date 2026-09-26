import React from 'react';
import { ShieldCheck, Plus } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionText,
  onAction,
  icon,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3.5rem 1.5rem',
        textAlign: 'center',
        background: 'var(--bg-card)',
        borderRadius: '8px',
        border: '1px solid var(--border-color)',
      }}
    >
      <div
        style={{
          width: '54px',
          height: '54px',
          borderRadius: '50%',
          background: 'rgba(6, 182, 212, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--accent-cyan)',
          marginBottom: '1rem',
        }}
      >
        {icon || <ShieldCheck size={28} />}
      </div>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-bright)', marginBottom: '0.35rem' }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: '420px', marginBottom: actionText ? '1.25rem' : '0' }}>
        {description}
      </p>
      {actionText && onAction && (
        <button type="button" className="btn btn-primary" onClick={onAction}>
          <Plus size={16} />
          <span>{actionText}</span>
        </button>
      )}
    </div>
  );
};
