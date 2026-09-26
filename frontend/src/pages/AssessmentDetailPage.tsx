import React, { useEffect, useState, useRef } from 'react';
import { Assessment, SecurityCheck, Finding } from '../types/api';
import { StatCard } from '../components/common/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { TargetBadge } from '../components/common/TargetBadge';
import { ProgressIndicator } from '../components/assessment/ProgressIndicator';
import { CheckTable } from '../components/assessment/CheckTable';
import { FindingTable } from '../components/findings/FindingTable';
import { FindingDetailModal } from '../components/findings/FindingDetailModal';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import {
  ArrowLeft,
  Activity,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ShieldAlert,
  Server,
} from 'lucide-react';
import api from '../services/api';

interface AssessmentDetailPageProps {
  assessmentId: number;
  onBack: () => void;
}

export const AssessmentDetailPage: React.FC<AssessmentDetailPageProps> = ({
  assessmentId,
  onBack,
}) => {
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [checks, setChecks] = useState<SecurityCheck[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [generatingReport, setGeneratingReport] = useState<boolean>(false);
  const [reportGenMessage, setReportGenMessage] = useState<string | null>(null);

  const pollTimerRef = useRef<number | null>(null);

  const fetchAssessmentData = async (isInitial: boolean = false) => {
    if (isInitial) setLoading(true);
    try {
      const [assessmentData, checksData, findingsData] = await Promise.all([
        api.getAssessment(assessmentId),
        api.getChecks(assessmentId),
        api.getScanFindings(assessmentId),
      ]);

      setAssessment(assessmentData);
      setChecks(checksData || []);
      setFindings(findingsData || []);
      setError(null);

      // Continue polling if scan is still queued or running
      if (assessmentData.status === 'QUEUED' || assessmentData.status === 'RUNNING') {
        pollTimerRef.current = window.setTimeout(() => {
          fetchAssessmentData(false);
        }, 1500);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve assessment details');
    } finally {
      if (isInitial) setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssessmentData(true);

    return () => {
      if (pollTimerRef.current) {
        clearTimeout(pollTimerRef.current);
      }
    };
  }, [assessmentId]);

  if (loading) {
    return <LoadingState message={`Retrieving Assessment Session #${assessmentId}...`} />;
  }

  if (error || !assessment) {
    return <ErrorState message={error || 'Assessment not found'} onRetry={() => fetchAssessmentData(true)} />;
  }

  const handleGenerateReport = async (format: 'HTML' | 'PDF') => {
    setGeneratingReport(true);
    setReportGenMessage(null);
    try {
      const rep = await api.generateReport(assessmentId, format);
      setReportGenMessage(`Generated ${rep.report_type} report: ${rep.file_name}`);
      if (format === 'HTML') {
        window.open(api.getReportViewUrl(rep.id), '_blank');
      } else {
        window.open(api.getReportDownloadUrl(rep.id), '_blank');
      }
    } catch (err: any) {
      alert(`Failed to generate report: ${err.message}`);
    } finally {
      setGeneratingReport(false);
    }
  };

  const isDemo = assessment.target_type === 'DEMO';

  return (
    <div className="page-container">
      {/* Back button & Title Header */}
      <div className="page-header">
        <div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onBack}
            style={{ marginBottom: '0.85rem', padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
          >
            <ArrowLeft size={14} />
            <span>Back to Assessments</span>
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <h1 className="page-header-title">Assessment #{assessment.id}</h1>
            <StatusBadge status={assessment.status} />
            <TargetBadge targetType={assessment.target_type} />
          </div>
          <p className="page-header-desc" style={{ fontFamily: 'var(--font-mono)' }}>
            Target: <span style={{ color: 'var(--text-bright)' }}>{assessment.target_url}</span>
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
          <div style={{ textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <div>
              Duration:{' '}
              <strong style={{ color: 'var(--text-bright)', fontFamily: 'var(--font-mono)' }}>
                {assessment.duration_seconds !== null && assessment.duration_seconds !== undefined
                  ? `${assessment.duration_seconds.toFixed(2)}s`
                  : 'In Progress'}
              </strong>
            </div>
            {assessment.started_at && (
              <div style={{ marginTop: '0.2rem' }}>
                Started: {new Date(assessment.started_at).toLocaleTimeString()}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '0.4rem' }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => handleGenerateReport('HTML')}
              disabled={generatingReport}
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.78rem' }}
              title="Generate and Open HTML Report"
            >
              <span>{generatingReport ? 'Generating...' : 'Generate HTML Report'}</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => handleGenerateReport('PDF')}
              disabled={generatingReport}
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.78rem' }}
              title="Generate and Download PDF Report"
            >
              <span>Generate PDF</span>
            </button>
          </div>

          {reportGenMessage && (
            <div style={{ fontSize: '0.75rem', color: '#10b981', fontFamily: 'var(--font-mono)' }}>
              {reportGenMessage}
            </div>
          )}
        </div>
      </div>

      {/* Target Type Notice Banner */}
      {isDemo ? (
        <div
          style={{
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.35)',
            borderRadius: '6px',
            padding: '0.85rem 1.25rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          <ShieldAlert size={20} color="#f59e0b" style={{ flexShrink: 0 }} />
          <div style={{ fontSize: '0.85rem', color: '#fef3c7' }}>
            <strong>CONTROLLED DEMONSTRATION TARGET:</strong> This assessment was performed against the local testbed on port 9000. All detected weaknesses are synthetic demo findings and are not findings against World Monitor.
          </div>
        </div>
      ) : (
        <div
          style={{
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.35)',
            borderRadius: '6px',
            padding: '0.85rem 1.25rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          <Server size={20} color="var(--accent-cyan)" style={{ flexShrink: 0 }} />
          <div style={{ fontSize: '0.85rem', color: '#e0f2fe' }}>
            <strong>WORLD MONITOR — AUTHORIZED LOCAL INSTANCE:</strong> Assessment evaluated local application interface and verified source security controls.
          </div>
        </div>
      )}

      {/* Real-Time Live Progress Indicator */}
      <ProgressIndicator status={assessment.status} checks={checks} />

      {/* Assessment Check Stats */}
      <div className="stats-grid">
        <StatCard
          title="Total Checks"
          value={assessment.total_checks || checks.length}
          description="Evaluated check modules"
          icon={<Activity size={18} />}
          color="var(--accent-cyan)"
        />
        <StatCard
          title="Passed"
          value={assessment.passed_checks || 0}
          description="Controls active & verified"
          icon={<CheckCircle2 size={18} />}
          color="var(--status-pass)"
        />
        <StatCard
          title="Failed"
          value={assessment.failed_checks || 0}
          description="Detected weaknesses"
          icon={<XCircle size={18} />}
          color="var(--status-fail)"
        />
        <StatCard
          title="Manual Review"
          value={assessment.manual_checks || 0}
          description="Source & architectural audits"
          icon={<AlertCircle size={18} />}
          color="var(--status-manual)"
        />
        <StatCard
          title="Findings Count"
          value={findings.length}
          description="Identified vulnerabilities"
          icon={<ShieldAlert size={18} />}
          color="var(--sev-high)"
        />
      </div>

      {/* Severity Breakdown */}
      <div className="severity-grid">
        <div className="severity-card sev-card-critical">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-critical)' }}>CRITICAL</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
            {assessment.critical_findings || 0}
          </div>
        </div>
        <div className="severity-card sev-card-high">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-high)' }}>HIGH</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
            {assessment.high_findings || 0}
          </div>
        </div>
        <div className="severity-card sev-card-medium">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-medium)' }}>MEDIUM</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
            {assessment.medium_findings || 0}
          </div>
        </div>
        <div className="severity-card sev-card-low">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-low)' }}>LOW</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
            {assessment.low_findings || 0}
          </div>
        </div>
        <div className="severity-card sev-card-info">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-info)' }}>INFORMATIONAL</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
            {assessment.info_findings || 0}
          </div>
        </div>
      </div>

      {/* Identified Findings Section */}
      <div className="soc-card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div className="card-title">
            <ShieldAlert size={18} color="var(--sev-high)" />
            <span>Identified Vulnerability Findings ({findings.length})</span>
          </div>
        </div>
        <FindingTable findings={findings} onSelectFinding={(f) => setSelectedFinding(f)} />
      </div>

      {/* Detailed Checks Matrix */}
      <div className="soc-card">
        <div className="card-header">
          <div className="card-title">
            <Activity size={18} color="var(--accent-cyan)" />
            <span>Security Checks Execution Matrix ({checks.length})</span>
          </div>
        </div>
        <CheckTable checks={checks} assessmentId={assessment.id} />
      </div>

      {/* Finding Detail Modal */}
      <FindingDetailModal finding={selectedFinding} onClose={() => setSelectedFinding(null)} />
    </div>
  );
};
