import React, { useEffect, useState } from 'react';
import { Finding, Evidence } from '../../types/api';
import { SeverityBadge } from '../common/SeverityBadge';
import { StatusBadge } from '../common/StatusBadge';
import { EvidencePanel } from '../assessment/EvidencePanel';
import { X, ShieldAlert, Wrench, Terminal, AlertCircle, Info } from 'lucide-react';
import api from '../../services/api';

interface FindingDetailModalProps {
  finding: Finding | null;
  onClose: () => void;
}

export const FindingDetailModal: React.FC<FindingDetailModalProps> = ({ finding, onClose }) => {
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [loadingEvidence, setLoadingEvidence] = useState<boolean>(false);

  useEffect(() => {
    if (!finding) return;

    let isMounted = true;
    setLoadingEvidence(true);

    api
      .getEvidence(finding.assessment_id, finding.check_id || undefined, finding.id)
      .then((data) => {
        if (isMounted) setEvidenceList(data);
      })
      .catch((err) => {
        console.error('Failed to load finding evidence', err);
      })
      .finally(() => {
        if (isMounted) setLoadingEvidence(false);
      });

    return () => {
      isMounted = false;
    };
  }, [finding]);

  if (!finding) return null;

  const isDemoFinding =
    finding.title.includes('CONTROLLED DEMO') ||
    finding.description?.includes('CONTROLLED DEMO') ||
    finding.finding_code.includes('DEMO');

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <SeverityBadge severity={finding.severity} />
            <StatusBadge status={finding.status} />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {finding.finding_code}
            </span>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
            style={{ padding: '0.35rem', borderRadius: '50%' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Finding Title */}
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '0.4rem' }}>
              {finding.title}
            </h2>
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              <span>Category: <strong style={{ color: 'var(--text-primary)' }}>{finding.category}</strong></span>
              <span>•</span>
              <span>Assessment ID: <strong style={{ color: 'var(--accent-cyan)' }}>#{finding.assessment_id}</strong></span>
              <span>•</span>
              <span>Confidence: <strong style={{ color: 'var(--text-primary)' }}>{finding.confidence ? `${finding.confidence}%` : 'N/A'}</strong></span>
            </div>
          </div>

          {/* Controlled Demo Disclaimer Banner */}
          {isDemoFinding && (
            <div
              style={{
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                border: '1px solid rgba(245, 158, 11, 0.35)',
                borderRadius: '6px',
                padding: '0.75rem 1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
              }}
            >
              <ShieldAlert size={20} color="#f59e0b" style={{ flexShrink: 0 }} />
              <div style={{ fontSize: '0.82rem', color: '#fef3c7' }}>
                <strong>CONTROLLED DEMO FINDING — NOT A WORLDMONITOR FINDING</strong>
                <p style={{ marginTop: '0.2rem', color: '#fde68a' }}>
                  This vulnerability was detected in the isolated local demo target (port 9000) for assessment validation and does not represent a flaw in World Monitor.
                </p>
              </div>
            </div>
          )}

          {/* Affected Component */}
          {finding.affected_component && (
            <div className="soc-card" style={{ padding: '0.85rem 1rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                Affected Component
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                {finding.affected_component}
              </div>
            </div>
          )}

          {/* Description */}
          <div>
            <h4 style={{ fontSize: '0.9rem', color: 'var(--text-bright)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Info size={15} color="var(--accent-cyan)" />
              <span>Vulnerability Description</span>
            </h4>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {finding.description || 'No detailed description available.'}
            </p>
          </div>

          {/* Impact */}
          {finding.impact && (
            <div>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--text-bright)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <AlertCircle size={15} color="var(--sev-high)" />
                <span>Security Impact Analysis</span>
              </h4>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {finding.impact}
              </p>
            </div>
          )}

          {/* Technical Evidence */}
          <div>
            <h4 style={{ fontSize: '0.9rem', color: 'var(--text-bright)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Terminal size={15} color="#38bdf8" />
              <span>Technical Evidence</span>
            </h4>
            {loadingEvidence ? (
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '1rem 0' }}>
                Loading technical evidence...
              </div>
            ) : (
              <EvidencePanel evidenceList={evidenceList} />
            )}
          </div>

          {/* Reproduction Steps */}
          {finding.reproduction_steps && (
            <div>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--text-bright)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Terminal size={15} color="#a855f7" />
                <span>Reproduction Steps</span>
              </h4>
              <div className="evidence-box" style={{ color: '#cbd5e1' }}>
                {finding.reproduction_steps}
              </div>
            </div>
          )}

          {/* Remediation */}
          <div>
            <h4 style={{ fontSize: '0.9rem', color: 'var(--text-bright)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Wrench size={15} color="var(--status-pass)" />
              <span>Recommended Remediation</span>
            </h4>
            <div
              style={{
                backgroundColor: 'rgba(16, 185, 129, 0.08)',
                border: '1px solid rgba(16, 185, 129, 0.25)',
                borderRadius: '6px',
                padding: '0.85rem 1rem',
                fontSize: '0.875rem',
                color: '#d1fae5',
                lineHeight: 1.5,
              }}
            >
              {finding.remediation || 'Follow defensive engineering best practices to harden this component.'}
            </div>
          </div>

          {/* CVSS Evaluation */}
          <div className="soc-card" style={{ padding: '0.85rem 1rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
              CVSS v3.1 Scoring
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              {finding.cvss_score !== null && finding.cvss_score !== undefined ? (
                <span>
                  Score: <strong style={{ color: 'var(--text-bright)' }}>{finding.cvss_score}</strong> ({finding.cvss_vector || 'Vector N/A'})
                </span>
              ) : (
                <span style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>
                  CVSS assessment not yet assigned
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
