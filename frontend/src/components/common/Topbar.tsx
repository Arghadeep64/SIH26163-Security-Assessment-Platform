import { Database, RefreshCw } from 'lucide-react';

interface TopbarProps {
  pageTitle: string;
  dbConnected: boolean;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Topbar: React.FC<TopbarProps> = ({
  pageTitle,
  dbConnected,
  onRefresh,
  isRefreshing,
}) => {
  return (
    <header className="topbar">
      <div className="topbar-title-section">
        <h1 className="topbar-page-title">{pageTitle}</h1>
      </div>

      <div className="topbar-actions">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '6px',
            background: dbConnected ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            border: `1px solid ${dbConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            fontSize: '0.78rem',
            fontFamily: 'var(--font-mono)',
            color: dbConnected ? '#10b981' : '#ef4444',
          }}
        >
          <Database size={14} />
          <span>{dbConnected ? 'DB: CONNECTED' : 'DB: DISCONNECTED'}</span>
        </div>

        {onRefresh && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onRefresh}
            disabled={isRefreshing}
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
            title="Refresh Data"
          >
            <RefreshCw size={14} className={isRefreshing ? 'spin-animation' : ''} />
            <span>Refresh</span>
          </button>
        )}
      </div>
    </header>
  );
};
