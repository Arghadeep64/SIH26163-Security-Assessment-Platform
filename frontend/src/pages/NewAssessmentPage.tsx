import React, { useState } from 'react';
import { TargetType } from '../types/api';
import { ShieldAlert, ShieldCheck, Play, ArrowLeft, Info, AlertTriangle } from 'lucide-react';
import api from '../services/api';

interface NewAssessmentPageProps {
  onAssessmentCreated: (assessmentId: number) => void;
  onCancel: () => void;
}

export const NewAssessmentPage: React.FC<NewAssessmentPageProps> = ({
  onAssessmentCreated,
  onCancel,
}) => {
  const [targetUrl, setTargetUrl] = useState<string>('http://127.0.0.1:9000');
  const [targetType, setTargetType] = useState<TargetType>('DEMO');
  const [authorized, setAuthorized] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const isProductionTarget =
    targetUrl.toLowerCase().includes('worldmonitor.app') &&
    !targetUrl.toLowerCase().includes('localhost') &&
    !targetUrl.toLowerCase().includes('127.0.0.1');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authorized) {
      setErrorMessage('You must confirm authorization before initiating an assessment.');
      return;
    }

    if (isProductionTarget) {
      setErrorMessage(
        'Automated scanning of production worldmonitor.app is strictly prohibited by SIH26163 policy.'
      );
      return;
    }

    setSubmitting(true);
    setErrorMessage(null);

    try {
      const response = await api.createAssessment({
        target_url: targetUrl.trim(),
        target_type: targetType,
      });

      onAssessmentCreated(response.assessment_id);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to dispatch assessment request.');
      setSubmitting(false);
    }
  };

  return (
    <div className="page-container" style={{ maxWidth: '800px' }}>
      <div className="page-header">
        <div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            style={{ marginBottom: '1rem', padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
          >
            <ArrowLeft size={14} />
            <span>Back to Dashboard</span>
          </button>
          <h1 className="page-header-title">Initiate Security Assessment</h1>
          <p className="page-header-desc">
            Configure target parameters and confirm assessment authorization for SIH26163 evaluation.
          </p>
        </div>
      </div>

      {errorMessage && (
        <div
          style={{
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '6px',
            padding: '1rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            color: '#fca5a5',
            fontSize: '0.875rem',
          }}
        >
          <AlertTriangle size={20} color="var(--sev-critical)" style={{ flexShrink: 0 }} />
          <div>{errorMessage}</div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="soc-card" style={{ padding: '2rem' }}>
        {/* Target URL */}
        <div className="form-group">
          <label className="form-label" htmlFor="targetUrl">
            Target Host URL
          </label>
          <input
            id="targetUrl"
            type="url"
            required
            className="form-input"
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
            placeholder="http://127.0.0.1:9000"
            style={{ fontFamily: 'var(--font-mono)' }}
          />
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Default controlled demo target: <code style={{ color: 'var(--accent-cyan)' }}>http://127.0.0.1:9000</code>
          </span>
        </div>

        {/* Target Type */}
        <div className="form-group">
          <label className="form-label" htmlFor="targetType">
            Target Classification
          </label>
          <select
            id="targetType"
            className="form-select"
            value={targetType}
            onChange={(e) => setTargetType(e.target.value as TargetType)}
          >
            <option value="DEMO">CONTROLLED DEMO (Local Isolated Testbed - Port 9000)</option>
            <option value="LOCAL">LOCAL (World Monitor Development Instance)</option>
            <option value="AUTHORIZED_REMOTE">AUTHORIZED REMOTE (Authorized Staging Environment)</option>
          </select>
        </div>

        {/* Target Info Notice */}
        {targetType === 'DEMO' ? (
          <div
            style={{
              backgroundColor: 'rgba(245, 158, 11, 0.08)',
              border: '1px solid rgba(245, 158, 11, 0.25)',
              borderRadius: '6px',
              padding: '0.85rem 1rem',
              marginBottom: '1.5rem',
              fontSize: '0.82rem',
              color: '#fde68a',
              display: 'flex',
              gap: '0.6rem',
            }}
          >
            <Info size={16} color="#f59e0b" style={{ flexShrink: 0, marginTop: '0.1rem' }} />
            <div>
              <strong>Controlled Demo Target Selected:</strong> All vulnerabilities detected on port 9000 will be explicitly labeled as <code>[CONTROLLED DEMO FINDING — NOT A WORLDMONITOR FINDING]</code>.
            </div>
          </div>
        ) : (
          <div
            style={{
              backgroundColor: 'rgba(6, 182, 212, 0.08)',
              border: '1px solid rgba(6, 182, 212, 0.25)',
              borderRadius: '6px',
              padding: '0.85rem 1rem',
              marginBottom: '1.5rem',
              fontSize: '0.82rem',
              color: '#bae6fd',
              display: 'flex',
              gap: '0.6rem',
            }}
          >
            <ShieldCheck size={16} color="var(--accent-cyan)" style={{ flexShrink: 0, marginTop: '0.1rem' }} />
            <div>
              <strong>Local World Monitor Target:</strong> Assessment will audit both local HTTP interface and repository source patterns under <code>research/worldmonitor/</code>.
            </div>
          </div>
        )}

        {/* Production Warning Guard */}
        {isProductionTarget && (
          <div
            style={{
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              borderRadius: '6px',
              padding: '0.85rem 1rem',
              marginBottom: '1.5rem',
              fontSize: '0.82rem',
              color: '#fca5a5',
              display: 'flex',
              gap: '0.6rem',
            }}
          >
            <ShieldAlert size={18} color="var(--sev-critical)" style={{ flexShrink: 0 }} />
            <div>
              <strong>Safety Guard Triggered:</strong> Scanning live production domain <code>worldmonitor.app</code> is strictly blocked by the assessment engine safety client.
            </div>
          </div>
        )}

        {/* Mandatory Authorization Checkbox */}
        <div
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '1.15rem',
            marginBottom: '1.75rem',
          }}
        >
          <label
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.75rem',
              cursor: 'pointer',
            }}
          >
            <input
              type="checkbox"
              checked={authorized}
              onChange={(e) => setAuthorized(e.target.checked)}
              style={{
                width: '18px',
                height: '18px',
                marginTop: '0.15rem',
                accentColor: 'var(--accent-cyan)',
                cursor: 'pointer',
              }}
            />
            <div style={{ fontSize: '0.875rem', color: 'var(--text-bright)' }}>
              <strong>I confirm that I am authorized to assess this target.</strong>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Assessment operations adhere strictly to defensive, non-destructive methodologies in compliance with SIH26163 requirements.
              </div>
            </div>
          </label>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
          <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={submitting}>
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!authorized || isProductionTarget || submitting}
            style={{ padding: '0.7rem 1.5rem' }}
          >
            <Play size={16} />
            <span>{submitting ? 'Dispatching Scan...' : 'Start Assessment'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
