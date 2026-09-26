import { CheckCatalogItem } from '../types/api';

export const CHECKS_CATALOG: CheckCatalogItem[] = [
  {
    id: 'WEB-001',
    name: 'HTTP Security Headers',
    category: 'Web Security',
    type: 'AUTOMATED',
    description:
      'Evaluates presence of defensive edge headers: Content-Security-Policy, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and HSTS.',
    method: 'Safe GET Request on /',
    baseline: 'OWASP Secure Headers Project / NIST SP 800-95',
  },
  {
    id: 'WEB-002',
    name: 'CORS Policy & Origin Reflection',
    category: 'Web Security',
    type: 'AUTOMATED',
    description:
      'Tests preflight OPTIONS and GET responses with arbitrary origins to detect insecure wildcard configurations with credentials or unvalidated reflection.',
    method: 'Safe OPTIONS / GET Probes',
    baseline: 'W3C CORS Specification / OWASP ASVS 4.0 (V14.5.3)',
  },
  {
    id: 'WEB-003',
    name: 'Cookie Security Attributes',
    category: 'Web Security',
    type: 'AUTOMATED',
    description:
      'Inspects Set-Cookie headers for mandatory security attributes (HttpOnly, Secure, SameSite) with automated sensitive value redaction.',
    method: 'Safe GET Request with Token Sanitization',
    baseline: 'RFC 6265bis / OWASP Top 10 A05:2021',
  },
  {
    id: 'WEB-004',
    name: 'TLS / Transport Encryption',
    category: 'Web Security',
    type: 'AUTOMATED',
    description:
      'Verifies HTTPS transport encryption and evaluates HTTP-to-HTTPS upgrade behavior (handles local loopback environments gracefully).',
    method: 'Safe TLS Connection Handshake Check',
    baseline: 'NIST SP 800-52 Rev 2 / OWASP Transport Layer Guidelines',
  },
  {
    id: 'CONFIG-001',
    name: 'Information Disclosure in Responses',
    category: 'Configuration Security',
    type: 'AUTOMATED',
    description:
      'Detects unhandled stack traces, internal filesystem paths, server runtime headers (X-Powered-By), and verbose debug responses.',
    method: 'Safe Probes on Core Endpoints',
    baseline: 'OWASP Top 10 A05:2021 (Security Misconfiguration)',
  },
  {
    id: 'CONFIG-002',
    name: 'Security Configuration Review',
    category: 'Configuration Security',
    type: 'MANUAL',
    description:
      'Audits deployment configuration manifests (vercel.json, Tauri tauri.conf.json, Nginx directives) for declared security policies.',
    method: 'Static File Manifest Parsing',
    baseline: 'CIS Benchmark for Web Servers / Cloud Hardening Guide',
  },
  {
    id: 'SOURCE-001',
    name: 'Source Code Pattern & Sink Audit',
    category: 'Source Code Security',
    type: 'MANUAL',
    description:
      'Scans repository source for security-sensitive sinks (innerHTML, eval, Function, child_process) and flags locations requiring manual verification.',
    method: 'Static Regex / AST Pattern Matching',
    baseline: 'OWASP Top 10 A03:2021 (Injection) / ASVS 4.0 (V5)',
  },
  {
    id: 'DEP-001',
    name: 'Dependency & Supply Chain Inventory',
    category: 'Supply Chain',
    type: 'AUTOMATED',
    description:
      'Inventories package manifests (package.json, Cargo.toml) and verifies lockfile presence for reproducible, secure supply chain hygiene.',
    method: 'Manifest Inventory & Lockfile Integrity',
    baseline: 'NIST SP 800-161 / OWASP Software Component Verification Standard',
  },
  {
    id: 'API-001',
    name: 'Documented Public API Discovery',
    category: 'API Security',
    type: 'AUTOMATED',
    description:
      'Safely probes known public endpoints (/api/version, /api/health, /api/product-catalog) to confirm availability and JSON response contracts.',
    method: 'Safe GET Probes against Documented Routes',
    baseline: 'OWASP API Security Top 10 API9:2023 (Improper Assets Management)',
  },
  {
    id: 'API-004',
    name: 'Rate Limiting Policy Review',
    category: 'API Security',
    type: 'MANUAL',
    description:
      'Reviews server-side sliding window rate limiting configurations (Upstash Redis, Nginx limits) to protect against volumetric abuse.',
    method: 'Passive Configuration Review',
    baseline: 'OWASP API Security Top 10 API4:2023 (Unrestricted Resource Consumption)',
  },
  {
    id: 'AUTH-001',
    name: 'Authentication Architecture Review',
    category: 'Authentication',
    type: 'MANUAL',
    description:
      'Audits authentication mechanisms across anonymous session tokens (wms_), user API keys (wm_), Clerk JWTs, and sidecar bearer tokens.',
    method: 'Architectural Source & Header Checklist',
    baseline: 'OWASP ASVS 4.0 (V2 Authentication) / NIST SP 800-63B',
  },
  {
    id: 'AUTHZ-001',
    name: 'Authorization & Entitlement Review',
    category: 'Authorization',
    type: 'MANUAL',
    description:
      'Evaluates role boundaries and tier entitlements (Free, Pro, Enterprise) across domain RPC routes to prevent Broken Object Level Authorization.',
    method: 'RPC Route Entitlement Matrix Review',
    baseline: 'OWASP API Security Top 10 API1:2023 (BOLA) & API5:2023 (BFLA)',
  },
  {
    id: 'SSRF-001',
    name: 'SSRF Defense & Proxy Validation',
    category: 'Network Security',
    type: 'MANUAL',
    description:
      'Reviews server-side proxy implementations (rss-proxy.js, mcp-proxy.ts) for domain allowlisting, DoH DNS pre-validation, and IPv4 socket pinning.',
    method: 'Proxy Handler Logic & Socket Pinning Audit',
    baseline: 'OWASP Top 10 A10:2021 (Server-Side Request Forgery)',
  },
  {
    id: 'TAURI-001',
    name: 'Tauri Native Desktop Security Audit',
    category: 'Desktop Security',
    type: 'MANUAL',
    description:
      'Audits native desktop capabilities, OS Keyring credential storage, and Origin gating to ensure loopback requests cannot be forged.',
    method: 'Native Rust Source & Capability Review',
    baseline: 'Tauri Security Best Practices / Principle of Least Privilege',
  },
];
