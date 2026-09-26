import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ message = 'Loading assessment data...' }) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '4rem 1.5rem',
        textAlign: 'center',
      }}
    >
      <Loader2
        size={36}
        color="var(--accent-cyan)"
        style={{ animation: 'spin 1s linear infinite', marginBottom: '1rem' }}
      />
      <div style={{ fontSize: '0.95rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
        {message}
      </div>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
