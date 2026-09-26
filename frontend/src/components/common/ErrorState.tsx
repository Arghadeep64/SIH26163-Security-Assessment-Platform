import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Assessment Error',
  message,
  onRetry,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem 1.5rem',
        textAlign: 'center',
        background: 'rgba(239, 68, 68, 0.05)',
        border: '1px solid rgba(239, 68, 68, 0.25)',
        borderRadius: '8px',
      }}
    >
      <div
        style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          background: 'rgba(239, 68, 68, 0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--sev-critical)',
          marginBottom: '1rem',
        }}
      >
        <AlertCircle size={26} />
      </div>
      <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-bright)', marginBottom: '0.35rem' }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.875rem', color: '#fca5a5', maxWidth: '480px', marginBottom: onRetry ? '1.25rem' : '0' }}>
        {message}
      </p>
      {onRetry && (
        <button type="button" className="btn btn-secondary" onClick={onRetry}>
          <RefreshCw size={15} />
          <span>Retry Operation</span>
        </button>
      )}
    </div>
  );
};
