import React from 'react';
import { SecurityCheck, AssessmentStatus } from '../../types/api';
import { CHECKS_CATALOG } from '../../data/checksCatalog';
import { StatusBadge } from '../common/StatusBadge';
import { CheckCircle2, XCircle, AlertCircle, Clock, Loader2 } from 'lucide-react';

interface ProgressIndicatorProps {
  status: AssessmentStatus;
  checks: SecurityCheck[];
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ status, checks }) => {
  const isRunning = status === 'RUNNING' || status === 'QUEUED';

  // Map existing checks by check_id
  const checkResultsMap = new Map<string, SecurityCheck>();
  checks.forEach((chk) => {
    checkResultsMap.set(chk.check_id, chk);
  });

  const totalCatalogChecks = CHECKS_CATALOG.length;
  const completedCount = checks.length;
  const progressPercent = Math.min(
    100,
    status === 'COMPLETED'
      ? 100
      : Math.round((completedCount / totalCatalogChecks) * 100)
  );

  return (
    <div className="soc-card" style={{ marginBottom: '1.5rem' }}>
      <div className="card-header">
        <div className="card-title">
          {isRunning ? (
            <Loader2 size={18} color="var(--accent-cyan)" style={{ animation: 'spin 1s linear infinite' }} />
          ) : (
            <CheckCircle2 size={18} color="var(--status-pass)" />
          )}
          <span>
            {isRunning
              ? 'Scan Execution in Progress'
              : status === 'COMPLETED'
              ? 'Assessment Execution Completed'
              : `Scan Status: ${status}`}
          </span>
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
          {completedCount} / {totalCatalogChecks} Checks Evaluated ({progressPercent}%)
        </div>
      </div>

      {/* Progress Bar */}
      <div
        style={{
          width: '100%',
          height: '6px',
          backgroundColor: 'var(--bg-input)',
          borderRadius: '3px',
          overflow: 'hidden',
          marginBottom: '1.25rem',
        }}
      >
        <div
          style={{
            width: `${progressPercent}%`,
            height: '100%',
            background: isRunning
              ? 'linear-gradient(90deg, #06b6d4, #3b82f6)'
              : '#10b981',
            transition: 'width 0.4s ease',
          }}
        />
      </div>

      {/* Checks Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '0.65rem',
        }}
      >
        {CHECKS_CATALOG.map((catItem) => {
          const result = checkResultsMap.get(catItem.id);

          return (
            <div
              key={catItem.id}
              style={{
                backgroundColor: '#0a0f1c',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '0.65rem 0.85rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '0.5rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0 }}>
                {result ? (
                  result.status === 'PASS' ? (
                    <CheckCircle2 size={16} color="var(--status-pass)" />
                  ) : result.status === 'FAIL' ? (
                    <XCircle size={16} color="var(--status-fail)" />
                  ) : result.status === 'MANUAL' ? (
                    <AlertCircle size={16} color="var(--status-manual)" />
                  ) : (
                    <XCircle size={16} color="var(--sev-critical)" />
                  )
                ) : isRunning ? (
                  <Loader2 size={14} color="var(--text-muted)" style={{ animation: 'spin 1.5s linear infinite' }} />
                ) : (
                  <Clock size={14} color="var(--text-muted)" />
                )}

                <div style={{ minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: '0.78rem',
                      fontWeight: 600,
                      fontFamily: 'var(--font-mono)',
                      color: 'var(--text-bright)',
                    }}
                  >
                    {catItem.id}
                  </div>
                  <div
                    style={{
                      fontSize: '0.74rem',
                      color: 'var(--text-secondary)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                    title={catItem.name}
                  >
                    {catItem.name}
                  </div>
                </div>
              </div>

              <div>
                {result ? (
                  <StatusBadge status={result.status} />
                ) : (
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    PENDING
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
