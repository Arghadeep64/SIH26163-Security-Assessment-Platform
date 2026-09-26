import React, { useEffect, useState } from 'react';
import { Assessment } from '../types/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { TargetBadge } from '../components/common/TargetBadge';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { History, ShieldPlus, ArrowRight, RefreshCw } from 'lucide-react';
import api from '../services/api';

interface AssessmentsListPageProps {
  onSelectAssessment: (id: number) => void;
  onNavigateNewAssessment: () => void;
}

export const AssessmentsListPage: React.FC<AssessmentsListPageProps> = ({
  onSelectAssessment,
  onNavigateNewAssessment,
}) => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAssessments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAssessments(50);
      setAssessments(data);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve assessment history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssessments();
  }, []);

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-header-title">Assessment History</h1>
          <p className="page-header-desc">
            Chronological audit trail of all executed security assessments against authorized targets.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={fetchAssessments}
            disabled={loading}
            style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem' }}
          >
            <RefreshCw size={14} className={loading ? 'spin-animation' : ''} />
            <span>Refresh</span>
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={onNavigateNewAssessment}
            style={{ padding: '0.45rem 1rem', fontSize: '0.8rem' }}
          >
            <ShieldPlus size={15} />
            <span>New Assessment</span>
          </button>
        </div>
      </div>

      {loading ? (
        <LoadingState message="Loading assessment sessions..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchAssessments} />
      ) : assessments.length === 0 ? (
        <EmptyState
          title="No Assessment Sessions Found"
          description="You have not launched any security scans yet. Start an assessment to audit your targets."
          actionText="Launch Assessment"
          onAction={onNavigateNewAssessment}
          icon={<History size={28} />}
        />
      ) : (
        <div className="soc-card">
          <div className="card-header">
            <div className="card-title">
              <History size={18} color="var(--accent-cyan)" />
              <span>Assessment Sessions Registry ({assessments.length})</span>
            </div>
          </div>

          <div className="soc-table-container">
            <table className="soc-table">
              <thead>
                <tr>
                  <th>Session ID</th>
                  <th>Target Host</th>
                  <th>Classification</th>
                  <th>Status</th>
                  <th>Checks (P / F / M)</th>
                  <th>Findings</th>
                  <th>Duration</th>
                  <th>Initiated</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {assessments.map((a) => (
                  <tr key={a.id} onClick={() => onSelectAssessment(a.id)}>
                    <td>
                      <span
                        style={{
                          fontFamily: 'var(--font-mono)',
                          fontWeight: 700,
                          color: 'var(--accent-cyan)',
                        }}
                      >
                        #{a.id}
                      </span>
                    </td>
                    <td>
                      <div
                        style={{
                          fontFamily: 'var(--font-mono)',
                          fontSize: '0.85rem',
                          fontWeight: 600,
                          color: 'var(--text-bright)',
                        }}
                      >
                        {a.target_url}
                      </div>
                    </td>
                    <td>
                      <TargetBadge targetType={a.target_type} />
                    </td>
                    <td>
                      <StatusBadge status={a.status} />
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                        {a.total_checks || 0} (
                        <span style={{ color: 'var(--status-pass)' }}>{a.passed_checks || 0}</span> /{' '}
                        <span style={{ color: 'var(--status-fail)' }}>{a.failed_checks || 0}</span> /{' '}
                        <span style={{ color: 'var(--status-manual)' }}>{a.manual_checks || 0}</span>)
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.3rem' }}>
                        {(a.critical_findings || 0) > 0 && (
                          <span className="badge badge-critical">{a.critical_findings}C</span>
                        )}
                        {(a.high_findings || 0) > 0 && (
                          <span className="badge badge-high">{a.high_findings}H</span>
                        )}
                        {(a.medium_findings || 0) > 0 && (
                          <span className="badge badge-medium">{a.medium_findings}M</span>
                        )}
                        {(a.low_findings || 0) > 0 && (
                          <span className="badge badge-low">{a.low_findings}L</span>
                        )}
                        {(a.critical_findings || 0) === 0 &&
                          (a.high_findings || 0) === 0 &&
                          (a.medium_findings || 0) === 0 &&
                          (a.low_findings || 0) === 0 && (
                            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>0</span>
                          )}
                      </div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {a.duration_seconds !== null && a.duration_seconds !== undefined
                          ? `${a.duration_seconds.toFixed(2)}s`
                          : '—'}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                        {a.created_at ? new Date(a.created_at).toLocaleString() : '—'}
                      </span>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectAssessment(a.id);
                        }}
                        style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
                      >
                        <span>View</span>
                        <ArrowRight size={12} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
