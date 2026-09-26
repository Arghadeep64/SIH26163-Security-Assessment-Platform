import React, { useEffect, useState } from 'react';
import { Assessment, Finding } from '../types/api';
import { StatCard } from '../components/common/StatCard';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { StatusBadge } from '../components/common/StatusBadge';
import { TargetBadge } from '../components/common/TargetBadge';
import { EmptyState } from '../components/common/EmptyState';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { FindingDetailModal } from '../components/findings/FindingDetailModal';
import {
  ShieldCheck,
  ShieldAlert,
  ShieldPlus,
  History,
  Activity,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Server,
  ArrowRight,
} from 'lucide-react';
import api from '../services/api';

interface DashboardPageProps {
  onNavigateNewAssessment: () => void;
  onNavigateAssessmentDetail: (id: number) => void;
  onNavigateAssessmentsList: () => void;
  onNavigateFindings: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigateNewAssessment,
  onNavigateAssessmentDetail,
  onNavigateAssessmentsList,
  onNavigateFindings,
}) => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [targetOnline, setTargetOnline] = useState<boolean | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [scansData, findingsData] = await Promise.all([
        api.getAssessments(10),
        api.getFindings(undefined, undefined, 10),
      ]);
      setAssessments(scansData);
      setFindings(findingsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }

    // Check default demo target liveness
    try {
      const isAlive = await api.checkTargetLiveness('http://127.0.0.1:9000/health');
      setTargetOnline(isAlive);
    } catch {
      setTargetOnline(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return <LoadingState message="Loading SOC Dashboard metrics..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={loadData} />;
  }

  // Aggregate stats across all completed assessments
  const totalAssessments = assessments.length;
  let totalChecks = 0;
  let totalPassed = 0;
  let totalFailed = 0;
  let totalManual = 0;

  let totalCritical = 0;
  let totalHigh = 0;
  let totalMedium = 0;
  let totalLow = 0;
  let totalInfo = 0;

  findings.forEach((f) => {
    const s = f.severity?.toUpperCase();
    if (s === 'CRITICAL') totalCritical++;
    else if (s === 'HIGH') totalHigh++;
    else if (s === 'MEDIUM') totalMedium++;
    else if (s === 'LOW') totalLow++;
    else if (s === 'INFO') totalInfo++;
  });

  assessments.forEach((a) => {
    totalChecks += a.total_checks || 0;
    totalPassed += a.passed_checks || 0;
    totalFailed += a.failed_checks || 0;
    totalManual += a.manual_checks || 0;
  });

  return (
    <div className="page-container">
      {/* Target Status Card Banner */}
      <div className="target-banner-card">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
            <Server size={18} color="var(--accent-cyan)" />
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
              Designated Assessment Target
            </span>
          </div>
          <div className="target-info-group">
            <div className="target-url-text">http://127.0.0.1:9000</div>
            <TargetBadge targetType="DEMO" />
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                fontSize: '0.78rem',
                color: targetOnline ? '#10b981' : '#f59e0b',
                fontFamily: 'var(--font-mono)',
                fontWeight: 600,
              }}
            >
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: targetOnline ? '#10b981' : '#f59e0b',
                }}
              />
              <span>{targetOnline ? 'ONLINE' : 'OFFLINE (Start Target)'}</span>
            </div>
          </div>
          <div className="target-meta-pills">
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Authorization: <strong style={{ color: '#10b981' }}>AUTHORIZED</strong>
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>•</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Target Mode: <strong>CONTROLLED DEMONSTRATION</strong>
            </span>
          </div>
        </div>

        <div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={onNavigateNewAssessment}
            style={{ gap: '0.5rem' }}
          >
            <ShieldPlus size={16} />
            <span>Launch Assessment</span>
          </button>
        </div>
      </div>

      {/* Global SOC Metric Stats Grid */}
      <div className="stats-grid">
        <StatCard
          title="Total Assessments"
          value={totalAssessments}
          description="Executed scan sessions"
          icon={<History size={18} />}
          color="var(--accent-cyan)"
        />
        <StatCard
          title="Checks Evaluated"
          value={totalChecks}
          description="Across all historical scans"
          icon={<Activity size={18} />}
          color="var(--text-bright)"
        />
        <StatCard
          title="Passed Checks"
          value={totalPassed}
          description="Verified security controls"
          icon={<CheckCircle2 size={18} />}
          color="var(--status-pass)"
        />
        <StatCard
          title="Failed Checks"
          value={totalFailed}
          description="Detected security weaknesses"
          icon={<XCircle size={18} />}
          color="var(--status-fail)"
        />
        <StatCard
          title="Manual Reviews"
          value={totalManual}
          description="Checklists requiring audit"
          icon={<HelpCircle size={18} />}
          color="var(--status-manual)"
        />
      </div>

      {/* Severity Breakdown Section */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.75rem' }}>
          Identified Vulnerabilities by Severity
        </h3>
        <div className="severity-grid">
          <div className="severity-card sev-card-critical">
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-critical)' }}>CRITICAL</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{totalCritical}</div>
          </div>
          <div className="severity-card sev-card-high">
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-high)' }}>HIGH</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{totalHigh}</div>
          </div>
          <div className="severity-card sev-card-medium">
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-medium)' }}>MEDIUM</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{totalMedium}</div>
          </div>
          <div className="severity-card sev-card-low">
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-low)' }}>LOW</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{totalLow}</div>
          </div>
          <div className="severity-card sev-card-info">
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-info)' }}>INFORMATIONAL</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{totalInfo}</div>
          </div>
        </div>
      </div>

      {/* Two-Column Section: Recent Assessments & Recent Findings */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.5rem' }}>
        {/* Recent Assessments */}
        <div className="soc-card">
          <div className="card-header">
            <div className="card-title">
              <History size={16} color="var(--accent-cyan)" />
              <span>Recent Assessment Sessions</span>
            </div>
            {assessments.length > 0 && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onNavigateAssessmentsList}
                style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
              >
                <span>View All</span>
                <ArrowRight size={12} />
              </button>
            )}
          </div>

          {assessments.length === 0 ? (
            <EmptyState
              title="No Assessments Yet"
              description="Initiate your first authorized security assessment against the target."
              actionText="Start Scan"
              onAction={onNavigateNewAssessment}
            />
          ) : (
            <div className="soc-table-container">
              <table className="soc-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Target</th>
                    <th>Status</th>
                    <th>Checks</th>
                    <th>Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {assessments.slice(0, 5).map((a) => (
                    <tr key={a.id} onClick={() => onNavigateAssessmentDetail(a.id)}>
                      <td>
                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--accent-cyan)' }}>
                          #{a.id}
                        </span>
                      </td>
                      <td>
                        <div style={{ fontSize: '0.82rem', fontFamily: 'var(--font-mono)' }}>{a.target_url}</div>
                        <TargetBadge targetType={a.target_type} />
                      </td>
                      <td>
                        <StatusBadge status={a.status} />
                      </td>
                      <td>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                          {a.total_checks || 0}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          {a.duration_seconds !== null && a.duration_seconds !== undefined
                            ? `${a.duration_seconds.toFixed(1)}s`
                            : '—'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Identified Findings */}
        <div className="soc-card">
          <div className="card-header">
            <div className="card-title">
              <ShieldAlert size={16} color="var(--sev-high)" />
              <span>Identified Vulnerabilities</span>
            </div>
            {findings.length > 0 && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onNavigateFindings}
                style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
              >
                <span>View All</span>
                <ArrowRight size={12} />
              </button>
            )}
          </div>

          {findings.length === 0 ? (
            <div style={{ padding: '2.5rem 1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              <ShieldCheck size={32} color="var(--status-pass)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>No findings recorded yet.</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Run an assessment to populate detection results.
              </div>
            </div>
          ) : (
            <div className="soc-table-container">
              <table className="soc-table">
                <thead>
                  <tr>
                    <th>Severity</th>
                    <th>Finding Title</th>
                    <th>Category</th>
                  </tr>
                </thead>
                <tbody>
                  {findings.slice(0, 5).map((f) => (
                    <tr key={f.id} onClick={() => setSelectedFinding(f)}>
                      <td>
                        <SeverityBadge severity={f.severity} />
                      </td>
                      <td>
                        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-bright)' }}>
                          {f.title}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                          {f.finding_code}
                        </div>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{f.category}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Finding Detail Modal */}
      <FindingDetailModal finding={selectedFinding} onClose={() => setSelectedFinding(null)} />
    </div>
  );
};
