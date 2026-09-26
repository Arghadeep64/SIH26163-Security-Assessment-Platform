import React, { useEffect, useState } from 'react';
import { Report, ReportFormat } from '../types/api';
import { EmptyState } from '../components/common/EmptyState';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { FileText, Download, ExternalLink, RefreshCw, Plus, FileCode, Shield } from 'lucide-react';
import api from '../services/api';

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Quick report generation state
  const [inputAssessmentId, setInputAssessmentId] = useState<string>('');
  const [generatingFormat, setGeneratingFormat] = useState<ReportFormat>('HTML');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [genSuccessMessage, setGenSuccessMessage] = useState<string | null>(null);

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAllReports(50);
      setReports(data);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve generated reports');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    const id = parseInt(inputAssessmentId.trim(), 10);
    if (isNaN(id) || id <= 0) {
      setError('Please provide a valid Assessment ID.');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGenSuccessMessage(null);

    try {
      const newReport = await api.generateReport(id, generatingFormat);
      setGenSuccessMessage(
        `Successfully generated ${newReport.report_type} report for Assessment #${id} (${newReport.file_name}).`
      );
      setInputAssessmentId('');
      await fetchReports();
    } catch (err: any) {
      setError(err.message || 'Failed to generate assessment report');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-header-title">Assessment Reports</h1>
          <p className="page-header-desc">
            Executive dossiers, vulnerability technical evidence, and defensive remediation reports.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={fetchReports}
          disabled={loading}
          style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem' }}
        >
          <RefreshCw size={14} className={loading ? 'spin-animation' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Quick Generate Card */}
      <div className="soc-card" style={{ marginBottom: '1.5rem', padding: '1.25rem 1.5rem' }}>
        <div className="card-header" style={{ marginBottom: '0.85rem' }}>
          <div className="card-title">
            <Plus size={16} color="var(--accent-cyan)" />
            <span>Generate New Assessment Report</span>
          </div>
        </div>

        <form
          onSubmit={handleGenerateReport}
          style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', flexWrap: 'wrap' }}
        >
          <div style={{ flex: '1', minWidth: '180px' }}>
            <label className="form-label" style={{ fontSize: '0.78rem', marginBottom: '0.25rem' }}>
              Assessment ID
            </label>
            <input
              type="number"
              min="1"
              required
              className="form-input"
              value={inputAssessmentId}
              onChange={(e) => setInputAssessmentId(e.target.value)}
              placeholder="e.g. 1"
              style={{ padding: '0.45rem 0.75rem', fontSize: '0.85rem' }}
            />
          </div>

          <div style={{ width: '180px' }}>
            <label className="form-label" style={{ fontSize: '0.78rem', marginBottom: '0.25rem' }}>
              Report Format
            </label>
            <select
              className="form-select"
              value={generatingFormat}
              onChange={(e) => setGeneratingFormat(e.target.value as ReportFormat)}
              style={{ padding: '0.45rem 0.75rem', fontSize: '0.85rem' }}
            >
              <option value="HTML">HTML Report (Interactive)</option>
              <option value="PDF">PDF Report (Printable)</option>
            </select>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={isGenerating || !inputAssessmentId}
            style={{ padding: '0.5rem 1.25rem' }}
          >
            <FileText size={15} />
            <span>{isGenerating ? 'Generating...' : `Generate ${generatingFormat}`}</span>
          </button>
        </form>

        {genSuccessMessage && (
          <div
            style={{
              marginTop: '1rem',
              padding: '0.65rem 0.9rem',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '6px',
              color: '#6ee7b7',
              fontSize: '0.82rem',
            }}
          >
            {genSuccessMessage}
          </div>
        )}
      </div>

      {/* Reports List */}
      {loading ? (
        <LoadingState message="Loading generated reports catalog..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchReports} />
      ) : reports.length === 0 ? (
        <EmptyState
          title="No Reports Generated Yet"
          description="Generate your first HTML or PDF security report from an executed assessment session."
          icon={<FileText size={28} />}
        />
      ) : (
        <div className="soc-card">
          <div className="card-header">
            <div className="card-title">
              <Shield size={18} color="var(--accent-cyan)" />
              <span>Generated Security Reports Repository ({reports.length})</span>
            </div>
          </div>

          <div className="soc-table-container">
            <table className="soc-table">
              <thead>
                <tr>
                  <th>Report ID</th>
                  <th>Assessment</th>
                  <th>Format</th>
                  <th>Filename</th>
                  <th>Generated At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r) => (
                  <tr key={r.id}>
                    <td>
                      <span
                        style={{
                          fontFamily: 'var(--font-mono)',
                          fontWeight: 600,
                          color: 'var(--accent-cyan)',
                        }}
                      >
                        #{r.id}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                        Session #{r.assessment_id}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`badge ${
                          r.report_type === 'PDF' ? 'badge-critical' : 'badge-info'
                        }`}
                        style={{ fontSize: '0.72rem' }}
                      >
                        {r.report_type === 'PDF' ? <FileText size={11} /> : <FileCode size={11} />}
                        <span>{r.report_type}</span>
                      </span>
                    </td>
                    <td>
                      <div
                        style={{
                          fontFamily: 'var(--font-mono)',
                          fontSize: '0.8rem',
                          color: 'var(--text-bright)',
                        }}
                      >
                        {r.file_name}
                      </div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                        {r.generated_at
                          ? new Date(r.generated_at).toLocaleString()
                          : r.created_at
                          ? new Date(r.created_at).toLocaleString()
                          : '—'}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.4rem' }}>
                        {r.report_type === 'HTML' ? (
                          <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={() => window.open(api.getReportViewUrl(r.id), '_blank')}
                            style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem' }}
                            title="Open HTML Report in New Tab"
                          >
                            <ExternalLink size={12} />
                            <span>Open HTML</span>
                          </button>
                        ) : (
                          <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={() => window.open(api.getReportViewUrl(r.id), '_blank')}
                            style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem' }}
                            title="Open PDF Preview in New Tab"
                          >
                            <ExternalLink size={12} />
                            <span>Preview</span>
                          </button>
                        )}
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => window.open(api.getReportDownloadUrl(r.id), '_blank')}
                          style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem' }}
                          title="Download Report File"
                        >
                          <Download size={12} />
                          <span>Download</span>
                        </button>
                      </div>
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
