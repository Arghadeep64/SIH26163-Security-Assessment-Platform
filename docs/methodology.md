# Assessment Methodology: SIH26163 Platform

- **Project ID:** SIH26163
- **Platform:** Automated Defensive Security Assessment Platform
- **Target Application:** World Monitor (Local / Authorized Test Instances) & SIH26163 Controlled Demo Target
- **Status:** Phase 5 Controlled Demo Target & Workflow Validation

---

## 1. Principles of Defensive Assessment

The SIH26163 Security Assessment Engine is designed strictly for authorized, defensive evaluation. The scanner adheres to the following core operational principles:

1. **Strict Target Authorization**: Network checks only execute against explicitly authorized local instances (`localhost`, `127.0.0.1`), controlled staging environments, or demo targets.
2. **No Production Attack Vectors**: Automated testing against `https://www.worldmonitor.app` is strictly blocked by engine safety guards.
3. **Non-Destructive Operations**: Only safe, bounded HTTP methods (`GET`, `HEAD`, `OPTIONS`) are utilized during automated discovery. No data alteration, brute-force requests, denial-of-service floods, or state-changing payloads are executed.
4. **Mandatory Redaction**: All captured request and response evidence is automatically sanitized to redact API keys, session tokens, passwords, and private credentials before database persistence.

---

## 2. Assessment Workflow

```text
Target Input (Authorized URL + Source Path)
       │
       ▼
1. Passive & Source Code Analysis
   • Pattern audit across research/worldmonitor/ (DOM sinks, innerHTML, eval)
   • Configuration inspection (vercel.json, tauri.conf.json, nginx headers)
   • Supply chain & dependency manifest audit (package.json, Cargo.toml)
   • SSRF defense validation (rss-proxy.js, mcp-proxy.ts, sidecar IPv4 pinning)
       │
       ▼
2. Safe HTTP Assessment
   • HTTP Security Headers (CSP, HSTS, X-Content-Type-Options, Referrer-Policy)
   • CORS Preflight & Origin Reflection Analysis
   • Cookie Security Attribute Inspection (HttpOnly, Secure, SameSite)
   • TLS/HTTPS Transport Encryption Evaluation
   • Information Disclosure & Debug Metadata Probing
   • Documented Public API Discovery
       │
       ▼
3. Evidence Collection & Redaction
   • Automated sanitization of tokens, credentials, and sensitive headers
   • Technical evidence linked to assessment, check, and finding records
       │
       ▼
4. Finding Classification & Severity Scoring
   • Clear distinction: PASS, OBSERVATION, POTENTIAL_ISSUE, CONFIRMED, MANUAL_VERIFICATION
   • Conservative severity assignment (INFO, LOW, MEDIUM, HIGH, CRITICAL)
   • Prevention of speculative CVSS scoring
       │
       ▼
5. Result Persistence & Reporting
   • MySQL / TiDB relational storage (assessments, checks, findings, evidence)
   • Real-time REST API for scan monitoring and findings retrieval
```

---

## 3. Evaluation Modules & Implemented Checks

| Check ID | Module Name | Method | Purpose & Evaluation |
| :--- | :--- | :--- | :--- |
| **WEB-001** | Security Headers | Safe GET | Verifies CSP, HSTS, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy. |
| **WEB-002** | CORS Policy | Safe OPTIONS / GET | Tests origin reflection and credentials allowance against arbitrary origins. |
| **WEB-003** | Cookie Security | Safe GET | Evaluates Set-Cookie headers for HttpOnly, Secure, and SameSite flags (with redacted values). |
| **WEB-004** | TLS / Transport | Safe Connection | Assesses transport encryption (handles local HTTP loopback without false alarms). |
| **CONFIG-001**| Information Disclosure| Safe Probes | Detects server stack traces, unhandled debug exceptions, or exposed runtime metadata. |
| **CONFIG-002**| Security Configuration| Source Audit | Reviews vercel.json, Nginx rules, and Tauri config for declared security directives. |
| **SOURCE-001**| Source Code Sinks | Static Regex / AST | Audits repository source for sensitive sinks (`innerHTML`, `eval`, `child_process`). |
| **DEP-001** | Dependency Inventory | Manifest Audit | Evaluates package.json, Cargo.toml, and lockfile presence for software supply chain hygiene. |
| **API-001** | Safe API Discovery | Safe GET Probes | Validates availability and response contracts of documented public endpoints. |
| **API-004** | Rate Limiting Policy | Passive Review | Reviews Upstash Redis sliding window policies; flags active flood testing for staging. |
| **AUTH-001** | Authentication Review| Source Checklist | Details anonymous `wms_` tokens, user `wm_` keys, Clerk JWTs, and sidecar tokens. |
| **AUTHZ-001**| Authorization Review | Source Checklist | Reviews Free, Pro, and Enterprise entitlement boundaries across Sebuf RPC domain routes. |
| **SSRF-001** | SSRF Defense Review | Source Audit | Verifies domain allowlisting, DoH pre-flight DNS checks, and IPv4 socket pinning in proxies. |
| **TAURI-001** | Tauri Desktop Audit | Native Source Audit| Audits window origin gating, OS Keyring vault storage, and capability sandboxing. |

---

## 4. Controlled Demonstration Environment

To ensure complete end-to-end testing of the assessment platform without attacking production infrastructure or modifying World Monitor source code, Phase 5 introduces the **SIH26163 Controlled Demo Target** (`demo-target/`).

### Purpose and Boundaries
1. **Validation Testbed**: Exists solely to validate that the assessment workflow functions reliably from target initialization to finding generation, evidence capture, redaction, severity assignment, and persistence.
2. **Explicit Isolation**: The demo target runs independently on `http://127.0.0.1:9000` with clear disclaimer banners on all responses.
3. **Synthetic Weaknesses**: Contains four harmless, controlled security weaknesses:
   - Missing security headers (CSP, X-Content-Type-Options, Referrer-Policy omitted).
   - Permissive CORS on non-sensitive demo data (`/api/demo-data`).
   - Insecure demo cookie configuration (`demo_session=controlled-demo-value`).
   - Controlled diagnostic information disclosure (`/api/demo-error` with fake internal paths).
4. **Strict Labeling**: All vulnerabilities detected within the demo target are explicitly prefixed:
   `"[CONTROLLED DEMO FINDING — NOT A WORLDMONITOR FINDING]"`
   to prevent any conflation with the World Monitor target codebase.

---

## 5. Finding Classification

Every check executed by the engine assigns a rigorous classification status to its output:

### 1. `PASS`
- **Definition**: The security control is verified to be active, correctly configured, and effective according to industry best practices.
- **Action**: No remediation required. Recorded for compliance and security posture baseline.

### 2. `OBSERVATION`
- **Definition**: An informational finding or architectural characteristic that does not pose an immediate security risk but provides situational awareness (e.g., public API versioning formats or client-side caching headers).
- **Action**: Monitored during subsequent architecture updates.

### 3. `POTENTIAL ISSUE`
- **Definition**: A configuration, code pattern, or interface that exhibits suboptimal security hygiene or deviates from recommended hardening standards, but lacks deterministic proof of immediate exploitability (e.g., missing defence-in-depth headers or complex regex patterns in source sinks).
- **Action**: Recommended for hardening during routine development cycles.

### 4. `CONFIRMED FINDING`
- **Definition**: A deterministic, reproducible security flaw validated through direct technical evidence (e.g., arbitrary origin reflection with credentials enabled, unredacted diagnostic stack traces in responses, or cleartext cookie transmission).
- **Action**: Immediate remediation prioritized according to severity score (Low, Medium, High, Critical).

### 5. `MANUAL VERIFICATION`
- **Definition**: An architectural policy, static code pattern, or entitlement boundary that cannot be reliably confirmed through automated heuristics alone without risk of false positives (e.g., role-based authorization rules, dynamic SQL sanitizer callers, or rate-limiting thresholds).
- **Action**: Assigned to security engineers for contextual peer review in authorized staging environments.
