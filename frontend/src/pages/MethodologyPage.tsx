import React from 'react';
import {
  Shield,
  Search,
  CheckCircle2,
  Lock,
  AlertTriangle,
  Wrench,
  FileText,
  ShieldAlert,
} from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  const steps = [
    {
      num: '01',
      title: 'Authorized Target Input',
      icon: <Shield size={20} color="var(--accent-cyan)" />,
      desc: 'All security assessments strictly require explicit operator authorization. Automated scanning is permitted only against local loopback instances (localhost, 127.0.0.1) or isolated demo testbeds. Production scanning of worldmonitor.app is prohibited by engine guards.',
    },
    {
      num: '02',
      title: 'Non-Destructive Probing',
      icon: <Search size={20} color="#38bdf8" />,
      desc: 'Probing is strictly non-destructive. Network operations are bounded to safe HTTP verbs (GET, HEAD, OPTIONS). No brute force, payload fuzzing, or state-altering requests (POST/PUT/DELETE) are performed automatically.',
    },
    {
      num: '03',
      title: 'Baseline Security Checks',
      icon: <CheckCircle2 size={20} color="var(--status-pass)" />,
      desc: 'Fourteen modular evaluation modules evaluate edge headers (CSP, HSTS), CORS policies, cookie flags, TLS transport, debug leaks, source code sinks (innerHTML, eval), supply chain dependencies, and SSRF defenses.',
    },
    {
      num: '04',
      title: 'Evidence Collection & Mandatory Redaction',
      icon: <Lock size={20} color="#f59e0b" />,
      desc: 'Collected headers, responses, and source lines are automatically sanitized. Session tokens, API keys, and sensitive cookie values are stripped and replaced with [REDACTED_VALUE] before relational persistence.',
    },
    {
      num: '05',
      title: 'Finding Classification Standards',
      icon: <AlertTriangle size={20} color="var(--sev-high)" />,
      desc: 'Findings are categorized rigorously: PASS (verified active control), OBSERVATION (informational baseline), POTENTIAL_ISSUE (suboptimal hygiene), CONFIRMED (deterministic proof of vulnerability), and MANUAL_VERIFICATION (architectural review).',
    },
    {
      num: '06',
      title: 'Severity & Impact Scoring',
      icon: <ShieldAlert size={20} color="var(--sev-critical)" />,
      desc: 'Conservative severity classification (INFO, LOW, MEDIUM, HIGH, CRITICAL) prevents artificial inflation. CVSS v3.1 vectors are assigned only when supported by deterministic evidence.',
    },
    {
      num: '07',
      title: 'Actionable Defensive Remediation',
      icon: <Wrench size={20} color="var(--status-pass)" />,
      desc: 'Every identified weakness is accompanied by engineering remediation guidelines tailored to modern web frameworks, reverse proxies (Nginx/Vercel), and Tauri desktop architectures.',
    },
    {
      num: '08',
      title: 'Audit Persistence & Reporting',
      icon: <FileText size={20} color="#a855f7" />,
      desc: 'All assessment metadata, check telemetry, findings, and sanitized evidence are stored in MySQL/TiDB tables, enabling structured reporting and security posture monitoring over time.',
    },
  ];

  return (
    <div className="page-container" style={{ maxWidth: '1000px' }}>
      <div className="page-header">
        <div>
          <h1 className="page-header-title">Assessment Methodology</h1>
          <p className="page-header-desc">
            Defensive security evaluation principles and standardized verification lifecycle (SIH26163).
          </p>
        </div>
      </div>

      {/* Controlled Demonstration Target Card */}
      <div
        style={{
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '8px',
          padding: '1.25rem 1.5rem',
          marginBottom: '2rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
          <ShieldAlert size={20} color="#f59e0b" />
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#fef3c7' }}>
            Controlled Demonstration Environment (Port 9000)
          </h3>
        </div>
        <p style={{ fontSize: '0.875rem', color: '#fde68a', lineHeight: 1.6 }}>
          The isolated demo target (<code>http://127.0.0.1:9000</code>) exists solely to validate the end-to-end security assessment workflow. Weaknesses detected on port 9000 are synthetic demonstration flaws and are not findings against World Monitor. World Monitor source repository code under <code>research/worldmonitor/</code> is never modified.
        </p>
      </div>

      {/* 8 Methodology Pillars */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {steps.map((s) => (
          <div
            key={s.num}
            className="soc-card"
            style={{
              display: 'flex',
              gap: '1.25rem',
              alignItems: 'flex-start',
              padding: '1.25rem 1.5rem',
            }}
          >
            <div
              style={{
                fontSize: '1.25rem',
                fontWeight: 800,
                fontFamily: 'var(--font-mono)',
                color: 'var(--accent-cyan)',
                opacity: 0.8,
                flexShrink: 0,
                width: '32px',
              }}
            >
              {s.num}
            </div>

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                {s.icon}
                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-bright)' }}>
                  {s.title}
                </h3>
              </div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {s.desc}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
