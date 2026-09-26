import React, { useState } from 'react';
import { CHECKS_CATALOG } from '../data/checksCatalog';
import { CheckCircle2, Terminal, Filter, Search } from 'lucide-react';

export const SecurityChecksPage: React.FC = () => {
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredChecks = CHECKS_CATALOG.filter((chk) => {
    if (typeFilter !== 'ALL' && chk.type !== typeFilter) return false;
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      chk.id.toLowerCase().includes(q) ||
      chk.name.toLowerCase().includes(q) ||
      chk.category.toLowerCase().includes(q) ||
      chk.description.toLowerCase().includes(q)
    );
  });

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-header-title">Security Checks Catalog</h1>
          <p className="page-header-desc">
            Standard assessment checks inventory designed for the World Monitor application baseline (SIH26163).
          </p>
        </div>
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
          <span style={{ fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase' }}>Filter By:</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Execution Mode:</label>
          <select
            className="form-select"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
          >
            <option value="ALL">All Modes (14 Checks)</option>
            <option value="AUTOMATED">Automated Network/Probing (6 Checks)</option>
            <option value="MANUAL">Source & Architecture Audit (8 Checks)</option>
          </select>
        </div>

        <div style={{ flex: 1, minWidth: '220px', position: 'relative' }}>
          <input
            type="text"
            className="form-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search checks by ID, name, or baseline..."
            style={{ width: '100%', padding: '0.4rem 0.75rem 0.4rem 2rem', fontSize: '0.8rem' }}
          />
          <Search
            size={14}
            color="var(--text-muted)"
            style={{ position: 'absolute', left: '0.65rem', top: '50%', transform: 'translateY(-50%)' }}
          />
        </div>
      </div>

      {/* Checks Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))',
          gap: '1.25rem',
        }}
      >
        {filteredChecks.map((chk) => {
          const isAutomated = chk.type === 'AUTOMATED';

          return (
            <div key={chk.id} className="soc-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '0.75rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 700,
                        fontSize: '0.95rem',
                        color: 'var(--accent-cyan)',
                      }}
                    >
                      {chk.id}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>• {chk.category}</span>
                  </div>

                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.3rem',
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      fontFamily: 'var(--font-mono)',
                      background: isAutomated ? 'rgba(16, 185, 129, 0.15)' : 'rgba(168, 85, 247, 0.15)',
                      color: isAutomated ? '#10b981' : '#c084fc',
                      border: `1px solid ${isAutomated ? 'rgba(16, 185, 129, 0.3)' : 'rgba(168, 85, 247, 0.3)'}`,
                    }}
                  >
                    {isAutomated ? <CheckCircle2 size={12} /> : <Terminal size={12} />}
                    <span>{chk.type}</span>
                  </span>
                </div>

                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-bright)', marginBottom: '0.5rem' }}>
                  {chk.name}
                </h3>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.55, marginBottom: '1rem' }}>
                  {chk.description}
                </p>
              </div>

              <div
                style={{
                  backgroundColor: '#0a0f1d',
                  borderRadius: '6px',
                  padding: '0.75rem',
                  border: '1px solid var(--border-color)',
                  fontSize: '0.75rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.3rem',
                }}
              >
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Method: </span>
                  <span style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{chk.method}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Standard: </span>
                  <span style={{ color: 'var(--accent-cyan)' }}>{chk.baseline}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
