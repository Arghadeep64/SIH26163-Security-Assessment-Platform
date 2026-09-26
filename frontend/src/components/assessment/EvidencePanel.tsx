import React from 'react';
import { Evidence } from '../../types/api';
import { ShieldAlert, FileCode, Server, Terminal, Lock } from 'lucide-react';

interface EvidencePanelProps {
  evidenceList: Evidence[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ evidenceList }) => {
  if (!evidenceList || evidenceList.length === 0) {
    return (
      <div style={{ padding: '1.25rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        No technical evidence records collected for this check.
      </div>
    );
  }

  const getEvidenceIcon = (type: string) => {
    switch (type) {
      case 'SOURCE_CODE':
        return <FileCode size={16} color="#38bdf8" />;
      case 'HTTP_HEADER':
      case 'HTTP_RESPONSE':
        return <Server size={16} color="#06b6d4" />;
      case 'CONFIGURATION':
        return <Terminal size={16} color="#a855f7" />;
      default:
        return <ShieldAlert size={16} color="#f59e0b" />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {evidenceList.map((ev) => (
        <div
          key={ev.id}
          style={{
            backgroundColor: '#0a0f1d',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '1rem',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.6rem',
              flexWrap: 'wrap',
              gap: '0.5rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {getEvidenceIcon(ev.evidence_type)}
              <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-bright)' }}>
                {ev.title || 'Technical Evidence'}
              </span>
              <span className="badge badge-info" style={{ fontSize: '0.68rem' }}>
                {ev.evidence_type}
              </span>
            </div>

            {ev.redacted && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem',
                  fontSize: '0.72rem',
                  color: '#fbbf24',
                  background: 'rgba(245, 158, 11, 0.15)',
                  padding: '0.15rem 0.45rem',
                  borderRadius: '3px',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 600,
                }}
              >
                <Lock size={12} />
                <span>SECRETS REDACTED</span>
              </div>
            )}
          </div>

          {ev.description && (
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '0.6rem' }}>
              {ev.description}
            </p>
          )}

          {ev.source_file && (
            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.75rem',
                color: 'var(--accent-cyan)',
                marginBottom: '0.5rem',
              }}
            >
              Source: {ev.source_file}
              {ev.source_line ? ` (Line ${ev.source_line})` : ''}
            </div>
          )}

          {ev.request_data && (
            <div style={{ marginBottom: '0.5rem' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.2rem' }}>
                Request Details
              </div>
              <div className="evidence-box" style={{ color: '#94a3b8' }}>
                {ev.request_data}
              </div>
            </div>
          )}

          {ev.response_data && (
            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.2rem' }}>
                Observed Response / Technical Output
              </div>
              <div className="evidence-box">{ev.response_data}</div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
