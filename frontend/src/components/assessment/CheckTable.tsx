import React, { useState } from 'react';
import { SecurityCheck, Evidence } from '../../types/api';
import { StatusBadge } from '../common/StatusBadge';
import { SeverityBadge } from '../common/SeverityBadge';
import { EvidencePanel } from './EvidencePanel';
import { ChevronDown, ChevronRight } from 'lucide-react';
import api from '../../services/api';

interface CheckTableProps {
  checks: SecurityCheck[];
  assessmentId: number;
}

export const CheckTable: React.FC<CheckTableProps> = ({ checks, assessmentId }) => {
  const [expandedCheckId, setExpandedCheckId] = useState<number | null>(null);
  const [evidenceMap, setEvidenceMap] = useState<Record<number, Evidence[]>>({});
  const [loadingEvidenceId, setLoadingEvidenceId] = useState<number | null>(null);

  const toggleExpand = async (check: SecurityCheck) => {
    if (expandedCheckId === check.id) {
      setExpandedCheckId(null);
      return;
    }

    setExpandedCheckId(check.id);

    // Fetch evidence if not already cached
    if (!evidenceMap[check.id]) {
      setLoadingEvidenceId(check.id);
      try {
        const evList = await api.getEvidence(assessmentId, check.id);
        setEvidenceMap((prev) => ({ ...prev, [check.id]: evList }));
      } catch (err) {
        console.error('Failed to load check evidence', err);
      } finally {
        setLoadingEvidenceId(null);
      }
    }
  };

  return (
    <div className="soc-table-container">
      <table className="soc-table">
        <thead>
          <tr>
            <th style={{ width: '40px' }}></th>
            <th>Check ID</th>
            <th>Category</th>
            <th>Title</th>
            <th>Status</th>
            <th>Severity</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {checks.map((chk) => {
            const isExpanded = expandedCheckId === chk.id;
            return (
              <React.Fragment key={chk.id}>
                <tr onClick={() => toggleExpand(chk)}>
                  <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                    {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  </td>
                  <td>
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 600,
                        color: 'var(--accent-cyan)',
                      }}
                    >
                      {chk.check_id}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: 'var(--text-secondary)' }}>{chk.category}</span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-bright)' }}>{chk.title}</div>
                    {chk.affected_component && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {chk.affected_component}
                      </div>
                    )}
                  </td>
                  <td>
                    <StatusBadge status={chk.status} />
                  </td>
                  <td>
                    <SeverityBadge severity={chk.severity} />
                  </td>
                  <td>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
                      {chk.confidence !== null && chk.confidence !== undefined
                        ? `${chk.confidence.toFixed(0)}%`
                        : '—'}
                    </span>
                  </td>
                </tr>

                {isExpanded && (
                  <tr>
                    <td
                      colSpan={7}
                      style={{
                        backgroundColor: '#0c1220',
                        padding: '1.25rem 1.5rem',
                        borderBottom: '1px solid var(--border-color)',
                      }}
                    >
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div>
                          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                            Evaluation Assessment Summary
                          </h4>
                          <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                            {chk.description || 'No detailed description recorded.'}
                          </p>
                        </div>

                        <div>
                          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                            Technical Evidence Records
                          </h4>
                          {loadingEvidenceId === chk.id ? (
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '0.5rem 0' }}>
                              Loading evidence...
                            </div>
                          ) : (
                            <EvidencePanel evidenceList={evidenceMap[chk.id] || []} />
                          )}
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
