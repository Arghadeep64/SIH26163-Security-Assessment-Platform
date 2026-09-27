import React, { useEffect, useState } from 'react';
import { Finding } from '../types/api';
import { FindingTable } from '../components/findings/FindingTable';
import { FindingDetailModal } from '../components/findings/FindingDetailModal';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { ShieldAlert, Filter, Search, RefreshCw } from 'lucide-react';
import api from '../services/api';

export const FindingsPage: React.FC = () => {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  const fetchFindings = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getFindings(
        severityFilter !== 'ALL' ? severityFilter : undefined,
        statusFilter !== 'ALL' ? statusFilter : undefined
      );
      setFindings(data);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve findings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFindings();
  }, [severityFilter, statusFilter]);

  const filteredFindings = findings.filter((f) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      f.title.toLowerCase().includes(q) ||
      f.finding_code.toLowerCase().includes(q) ||
      f.category.toLowerCase().includes(q) ||
      f.affected_component?.toLowerCase().includes(q)
    );
  });

  const confirmedVulnerabilities = filteredFindings.filter(
    (f) =>
      (f.status === 'CONFIRMED' || f.status === 'OPEN' || f.title.includes('CONTROLLED DEMO')) &&
      f.status !== 'ENVIRONMENT_OBSERVATION' &&
      f.status !== 'SOURCE_REVIEW' &&
      f.status !== 'INFORMATIONAL'
  );

  const securityObservations = filteredFindings.filter(
    (f) => !confirmedVulnerabilities.includes(f)
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-header-title">Vulnerability Findings</h1>
          <p className="page-header-desc">
            Comprehensive repository of identified security findings, evidence, and remediation guidelines.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={fetchFindings}
          disabled={loading}
          style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem' }}
        >
          <RefreshCw size={14} className={loading ? 'spin-animation' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div
        className="soc-card"
        style={{
          padding: '1rem 1.25rem',
          marginBottom: '1.5rem',
          display: 'flex',
          gap: '1rem',
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-secondary)' }}>
          <Filter size={16} />
          <span style={{ fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase' }}>Filters:</span>
        </div>

        {/* Severity Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Severity:</label>
          <select
            className="form-select"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
            <option value="INFO">Informational</option>
          </select>
        </div>

        {/* Status Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Status:</label>
          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
          >
            <option value="ALL">All Statuses</option>
            <option value="CONFIRMED">Confirmed</option>
            <option value="MANUAL_VERIFICATION">Manual Verification</option>
            <option value="OPEN">Open</option>
            <option value="REMEDIATED">Remediated</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>
        </div>

        {/* Search Filter */}
        <div style={{ flex: 1, minWidth: '220px', position: 'relative' }}>
          <input
            type="text"
            className="form-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by title, code, category..."
            style={{ width: '100%', padding: '0.4rem 0.75rem 0.4rem 2rem', fontSize: '0.8rem' }}
          />
          <Search
            size={14}
            color="var(--text-muted)"
            style={{ position: 'absolute', left: '0.65rem', top: '50%', transform: 'translateY(-50%)' }}
          />
        </div>
      </div>

      {/* Classification Summary Callout */}
      <div
        className="soc-card"
        style={{
          padding: '0.85rem 1.25rem',
          marginBottom: '1.25rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem',
          borderLeft: '4px solid var(--accent-cyan)',
        }}
      >
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          <strong style={{ color: 'var(--text-bright)' }}>SIH26163 Presentation Standard:</strong> Security observations (environment differences and documented source patterns) are strictly separated from confirmed exploitable vulnerabilities.
        </div>
        <div
          style={{
            fontSize: '0.8rem',
            color: '#10b981',
            fontWeight: 600,
            background: 'rgba(16, 185, 129, 0.1)',
            padding: '0.3rem 0.6rem',
            borderRadius: '4px',
          }}
        >
          No confirmed World Monitor vulnerability was established within the assessed scope and methodology.
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <LoadingState message="Querying findings repository..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchFindings} />
      ) : filteredFindings.length === 0 ? (
        <EmptyState
          title="No Findings Match Filter"
          description="There are no security findings currently matching your selected filters or search parameters."
          icon={<ShieldAlert size={28} />}
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Confirmed Vulnerabilities */}
          <div className="soc-card">
            <div className="card-header">
              <div className="card-title">
                <ShieldAlert size={18} color="var(--sev-high)" />
                <span>
                  Confirmed Vulnerabilities ({confirmedVulnerabilities.length})
                </span>
              </div>
            </div>
            {confirmedVulnerabilities.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                <div style={{ color: '#10b981', fontWeight: 600, fontSize: '0.95rem' }}>
                  Confirmed World Monitor Vulnerabilities: 0
                </div>
                <div style={{ fontSize: '0.82rem', marginTop: '0.25rem' }}>
                  No confirmed World Monitor vulnerability was established within the assessed scope and methodology.
                </div>
              </div>
            ) : (
              <FindingTable
                findings={confirmedVulnerabilities}
                onSelectFinding={(f) => setSelectedFinding(f)}
              />
            )}
          </div>

          {/* Security Observations */}
          <div className="soc-card">
            <div className="card-header">
              <div className="card-title">
                <ShieldAlert size={18} color="var(--accent-cyan)" />
                <span>
                  Security Observations &amp; Environment Notes ({securityObservations.length})
                </span>
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
                No security observations match current filter.
              </div>
            ) : (
              <FindingTable
                findings={securityObservations}
                onSelectFinding={(f) => setSelectedFinding(f)}
              />
            )}
          </div>
        </div>
      )}

      {/* Finding Detail Modal */}
      <FindingDetailModal finding={selectedFinding} onClose={() => setSelectedFinding(null)} />
    </div>
  );
};
