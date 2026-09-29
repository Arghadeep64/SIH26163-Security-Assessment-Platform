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
  Globe,
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

  const confirmedVulnerabilities = findings.filter(
    (f) =>
      (f.status === 'CONFIRMED' || f.status === 'OPEN' || isDemo) &&
      f.status !== 'ENVIRONMENT_OBSERVATION' &&
      f.status !== 'SOURCE_REVIEW' &&
      f.status !== 'INFORMATIONAL'
  );

  const securityObservations = findings.filter(
    (f) =>
      f.status === 'ENVIRONMENT_OBSERVATION' ||
      f.status === 'SOURCE_REVIEW' ||
      f.status === 'INFORMATIONAL' ||
      !confirmedVulnerabilities.includes(f)
  );

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
                  ? `${Number(assessment.duration_seconds).toFixed(2)}s`
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
      ) : assessment.target_type === 'AUTHORIZED_REMOTE' ? (
        <div
          style={{
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.35)',
            borderRadius: '6px',
            padding: '0.85rem 1.25rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          <Globe size={20} color="#60a5fa" style={{ flexShrink: 0 }} />
          <div style={{ fontSize: '0.85rem', color: '#dbeafe' }}>
            <strong>AUTHORIZED REMOTE TARGET:</strong> This assessment was performed against an authorized remote parity/demo target. Assessment operations evaluate public edge interfaces and remote security headers under authorized scope.
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
          title="Confirmed Vulns"
          value={confirmedVulnerabilities.length}
          description={isDemo ? 'Controlled demo weaknesses' : 'Confirmed application vulns'}
          icon={<ShieldAlert size={18} />}
          color={confirmedVulnerabilities.length > 0 ? 'var(--sev-high)' : 'var(--status-pass)'}
        />
        <StatCard
          title="Observations"
          value={securityObservations.length}
          description="Environment & source review"
          icon={<AlertCircle size={18} />}
          color="var(--accent-cyan)"
        />
      </div>

      {/* Finding Classification Callout Banner */}
      <div
        className="soc-card"
        style={{
          padding: '1rem 1.25rem',
          marginBottom: '1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          borderLeft: '4px solid var(--accent-cyan)',
        }}
      >
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            SIH26163 Finding Classification Summary
          </div>
          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-bright)', marginTop: '0.2rem' }}>
            Confirmed World Monitor Vulnerabilities: <span style={{ color: confirmedVulnerabilities.length > 0 ? 'var(--sev-high)' : '#10b981', fontFamily: 'var(--font-mono)' }}>{confirmedVulnerabilities.length}</span>
            <span style={{ margin: '0 0.5rem', color: 'var(--text-muted)' }}>&bull;</span>
            Security Observations: <span style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>{securityObservations.length}</span>
          </div>
        </div>
        {!isDemo && confirmedVulnerabilities.length === 0 && (
          <div
            style={{
              fontSize: '0.82rem',
              color: '#10b981',
              fontWeight: 600,
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              padding: '0.4rem 0.8rem',
              borderRadius: '4px',
            }}
          >
            No confirmed World Monitor vulnerability was established within the assessed scope and methodology.
          </div>
        )}
      </div>

      {/* Confirmed Vulnerabilities Section */}
      <div className="soc-card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div className="card-title">
            <ShieldAlert size={18} color={confirmedVulnerabilities.length > 0 ? 'var(--sev-high)' : '#10b981'} />
            <span>Confirmed Vulnerabilities ({confirmedVulnerabilities.length})</span>
          </div>
        </div>
        {confirmedVulnerabilities.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <CheckCircle2 size={32} color="#10b981" style={{ marginBottom: '0.5rem' }} />
            <div style={{ color: 'var(--text-bright)', fontWeight: 600 }}>
              Confirmed World Monitor Vulnerabilities: 0
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              No confirmed World Monitor vulnerability was established within the assessed scope and methodology.
            </div>
          </div>
        ) : (
          <FindingTable findings={confirmedVulnerabilities} onSelectFinding={(f) => setSelectedFinding(f)} />
        )}
      </div>

      {/* Security Observations Section */}
      <div className="soc-card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div className="card-title">
            <AlertCircle size={18} color="var(--accent-cyan)" />
            <span>Security Observations &amp; Environment Notes ({securityObservations.length})</span>
          </div>
          <span
            style={{
              fontSize: '0.72rem',
              padding: '0.2rem 0.55rem',
              background: 'rgba(6, 182, 212, 0.15)',
              color: 'var(--accent-cyan)',
              borderRadius: '4px',
              fontWeight: 600,
            }}
          >
            AUDIT OBSERVATIONS — NOT CONFIRMED VULNERABILITIES
          </span>
        </div>
        {securityObservations.length === 0 ? (
          <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            No security observations recorded for this session.
          </div>
        ) : (
          <FindingTable findings={securityObservations} onSelectFinding={(f) => setSelectedFinding(f)} />
        )}
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
