import React from 'react';
import { Finding } from '../../types/api';
import { SeverityBadge } from '../common/SeverityBadge';
import { StatusBadge } from '../common/StatusBadge';
import { ShieldAlert } from 'lucide-react';

interface FindingTableProps {
  findings: Finding[];
  onSelectFinding: (finding: Finding) => void;
}

export const FindingTable: React.FC<FindingTableProps> = ({ findings, onSelectFinding }) => {
  if (!findings || findings.length === 0) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No findings match the current filter criteria.
      </div>
    );
  }

  return (
    <div className="soc-table-container">
      <table className="soc-table">
        <thead>
          <tr>
            <th>Finding Code</th>
            <th>Title</th>
            <th>Category</th>
            <th>Severity</th>
            <th>Confidence</th>
            <th>Status</th>
            <th>Assessment</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f) => {
            const isDemo = f.title.includes('CONTROLLED DEMO');

            return (
              <tr key={f.id} onClick={() => onSelectFinding(f)}>
                <td>
                  <span
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 600,
                      color: 'var(--accent-cyan)',
                      fontSize: '0.8rem',
                    }}
                  >
                    {f.finding_code}
                  </span>
                </td>
                <td>
                  <div style={{ fontWeight: 600, color: 'var(--text-bright)' }}>
                    {f.title}
                  </div>
                  {isDemo && (
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.25rem',
                        fontSize: '0.7rem',
                        color: '#fbbf24',
                        marginTop: '0.2rem',
                        fontFamily: 'var(--font-mono)',
                      }}
                    >
                      <ShieldAlert size={12} />
                      <span>CONTROLLED DEMO TARGET</span>
                    </div>
                  )}
                </td>
                <td>
                  <span style={{ color: 'var(--text-secondary)' }}>{f.category}</span>
                </td>
                <td>
                  <SeverityBadge severity={f.severity} />
                </td>
                <td>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
                    {f.confidence !== null && f.confidence !== undefined ? `${f.confidence.toFixed(0)}%` : '—'}
                  </span>
                </td>
                <td>
                  <StatusBadge status={f.status} />
                </td>
                <td>
                  <span
                    style={{
                      fontFamily: 'var(--font-mono)',
                      color: 'var(--accent-cyan)',
                      fontWeight: 600,
                    }}
                  >
                    #{f.assessment_id}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
