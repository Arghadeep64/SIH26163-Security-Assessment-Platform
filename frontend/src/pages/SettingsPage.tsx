import React, { useEffect, useState } from 'react';
import { DatabaseHealthResponse, SystemHealthResponse } from '../types/api';
import { Database, Server, RefreshCw, Lock } from 'lucide-react';
import api from '../services/api';

export const SettingsPage: React.FC = () => {
  const [apiUrl, setApiUrl] = useState<string>(api.getBaseUrl());
  const [dbHealth, setDbHealth] = useState<DatabaseHealthResponse | null>(null);
  const [sysHealth, setSysHealth] = useState<SystemHealthResponse | null>(null);
  const [checking, setChecking] = useState<boolean>(false);

  const checkHealth = async () => {
    setChecking(true);
    try {
      const [db, sys] = await Promise.all([api.getDatabaseHealth(), api.getSystemHealth()]);
      setDbHealth(db);
      setSysHealth(sys);
    } catch (err) {
      setDbHealth({ status: 'unhealthy', database: 'disconnected' });
      setSysHealth({ status: 'offline' });
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="page-container" style={{ maxWidth: '850px' }}>
      <div className="page-header">
        <div>
          <h1 className="page-header-title">Platform Settings & Environment</h1>
          <p className="page-header-desc">
            Connectivity configuration, database persistence status, and scanner safety policy guards.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={checkHealth}
          disabled={checking}
          style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem' }}
        >
          <RefreshCw size={14} className={checking ? 'spin-animation' : ''} />
          <span>Check Health</span>
        </button>
      </div>

      {/* Backend API Configuration */}
      <div className="soc-card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div className="card-title">
            <Server size={18} color="var(--accent-cyan)" />
            <span>FastAPI Backend Connection</span>
          </div>
        </div>

        <div className="form-group" style={{ marginBottom: '0.5rem' }}>
          <label className="form-label">API Gateway Base URL</label>
          <input
            type="text"
            className="form-input"
            value={apiUrl}
            onChange={(e) => {
              setApiUrl(e.target.value);
              api.setBaseUrl(e.target.value);
            }}
            style={{ fontFamily: 'var(--font-mono)' }}
          />
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Configurable via <code>VITE_API_BASE_URL</code> environment variable (Default: http://127.0.0.1:8000).
          </span>
        </div>
      </div>

      {/* Database & Service Health */}
      <div className="soc-card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div className="card-title">
            <Database size={18} color="#10b981" />
            <span>Database & Service Health Check</span>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
          <div
            style={{
              backgroundColor: '#0a0f1d',
              padding: '1rem',
              borderRadius: '6px',
              border: '1px solid var(--border-color)',
            }}
          >
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              Database Persistence
            </div>
            <div
              style={{
                fontSize: '1rem',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                color: dbHealth?.database === 'connected' ? '#10b981' : '#ef4444',
              }}
            >
              {dbHealth ? (dbHealth.database === 'connected' ? 'CONNECTED' : 'DISCONNECTED') : 'CHECKING...'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              MySQL 8+ / TiDB relational schema
            </div>
          </div>

          <div
            style={{
              backgroundColor: '#0a0f1d',
              padding: '1rem',
              borderRadius: '6px',
              border: '1px solid var(--border-color)',
            }}
          >
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              Backend API Gateway
            </div>
            <div
              style={{
                fontSize: '1rem',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                color: sysHealth?.status === 'healthy' ? '#10b981' : '#ef4444',
              }}
            >
              {sysHealth ? sysHealth.status.toUpperCase() : 'CHECKING...'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              FastAPI Core Assessment Engine
            </div>
          </div>
        </div>
      </div>

      {/* Scanner Safety Rules Policy */}
      <div className="soc-card">
        <div className="card-header">
          <div className="card-title">
            <Lock size={18} color="var(--accent-cyan)" />
            <span>Active Safety Policies & Engine Constraints</span>
          </div>
        </div>

        <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          <li>
            <strong style={{ color: 'var(--text-bright)' }}>Production Target Protection:</strong> Automated network scanning against live domain <code>worldmonitor.app</code> is strictly blocked by SafeHttpClient.
          </li>
          <li>
            <strong style={{ color: 'var(--text-bright)' }}>Safe HTTP Verbs Only:</strong> Automated probes are restricted to non-state-altering methods (<code>GET</code>, <code>HEAD</code>, <code>OPTIONS</code>).
          </li>
          <li>
            <strong style={{ color: 'var(--text-bright)' }}>Automated Secrets Redaction:</strong> Bearer tokens, API keys (<code>wms_</code>, <code>wm_</code>), and sensitive cookie values are sanitized before storage.
          </li>
          <li>
            <strong style={{ color: 'var(--text-bright)' }}>No Code Modification:</strong> Target source under <code>research/worldmonitor/</code> is treated as read-only.
          </li>
        </ul>
      </div>
    </div>
  );
};
