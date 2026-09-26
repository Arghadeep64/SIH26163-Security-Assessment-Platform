# World Monitor: Comprehensive Security Assessment Test Matrix

- **Project:** SIH26163 (Security Assessment of World Monitor)
- **Target Baseline Commit:** `373294b1500c439de885ec86516a5d4c89c4e3b0`
- **Scope:** Test planning for subsequent automated/manual assessment phases.

---

## Security Assessment Test Matrix

| ID | Category | Target Component | Source Location | Security Test Description | Execution Mode | Dev Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AUTH-001** | Authentication | Anonymous Web Session | `api/wm-session.js`, `api/_session.js` | Verify HMAC-SHA256 signature enforcement, expiration checks, and rejection of forged `wms_` tokens. | Automated | **HIGH** |
| **AUTH-002** | Authentication | User API Keys | `api/_user-api-key.js`, `convex/http.ts` | Verify format enforcement (`wm_<40_hex>`), cache invalidation, and timing-safe comparisons. | Automated | **HIGH** |
| **AUTH-003** | Authentication | Enterprise API Keys | `api/_api-key.js`, `api/_crypto.js` | Test constant-time multi-key comparison against `WORLDMONITOR_VALID_KEYS`. | Automated | **MEDIUM** |
| **AUTH-004** | Authentication | Desktop Sidecar Token | `src-tauri/sidecar/local-api-server.mjs` | Test rejection of unauthenticated local requests lacking `x-worldmonitor-local-token`. | Automated | **HIGH** |
| **AUTHZ-001**| Authorization | Entitlement Enforcement | `server/_shared/entitlement-check.ts` | Verify access controls between Free, Pro, and Enterprise tiers on Sebuf RPC domain endpoints. | Automated | **HIGH** |
| **AUTHZ-002**| Authorization | Embed Panel Gating | `server/gateway.ts`, `shared/embed-access.ts` | Test token verification and route isolation for embedded map widgets (`EMBED_KEY_RPC_PATHS`). | Automated | **MEDIUM** |
| **AUTHZ-003**| Authorization | Internal Endpoints | `server/_shared/internal-auth.ts` | Verify rejection of unauthenticated or tampered requests to `/api/internal/*` without `RELAY_SHARED_SECRET`. | Automated | **HIGH** |
| **API-001** | API Security | Rate Limiting | `server/_shared/rate-limit.ts`, `api/_rate-limit.js` | Verify Upstash Redis sliding window enforcement, 429 status codes, and fail-open behavior. | Automated | **HIGH** |
| **API-002** | API Security | Idempotency Replay | `server/_shared/idempotency.ts` | Verify duplicate request suppression and cached response replay with `Idempotency-Key`. | Automated | **MEDIUM** |
| **API-003** | API Security | Request Schema Validation | `server/request-validator.ts`, `proto/` | Test rejection of malformed, unexpected, or deeply nested JSON-RPC payloads. | Automated | **MEDIUM** |
| **INPUT-001**| Input Validation | Coordinate & Bounding Box | `server/gateway.ts`, `api/geo.js` | Verify bounding box coordinate boundary parsing (`lat`, `lon`, `zoom`, `bbox`) against overflow/NaN inputs. | Automated | **MEDIUM** |
| **INPUT-002**| Input Validation | Search & Keyword Queries | `api/symbol-search.ts`, `api/ask.ts` | Test sanitization and length bounding of free-text search queries. | Automated | **LOW** |
| **SSRF-001** | SSRF Defense | RSS Proxy Domain Allowlist | `api/rss-proxy.js`, `api/_rss-allowed-domain-match.js` | Verify strict rejection of non-allowlisted domains and apex/www normalization integrity. | Automated | **HIGH** |
| **SSRF-002** | SSRF Defense | RSS Proxy Redirect Re-check | `api/rss-proxy.js` | Test that redirect hops (301/302) to non-allowlisted domains are blocked immediately. | Automated | **HIGH** |
| **SSRF-003** | SSRF Defense | MCP Proxy Pre-flight DNS | `api/mcp-proxy.ts` | Verify rejection of private/reserved IP addresses (RFC 1918, RFC 3927, loopback, cloud metadata). | Automated | **HIGH** |
| **SSRF-004** | SSRF Defense | Desktop Sidecar IPv4 Pinning | `src-tauri/sidecar/local-api-server.mjs` | Test socket lookup pinning and private IP rejection on local sidecar fetches. | Automated | **HIGH** |
| **CLIENT-001**| Client-Side | DOM Sanitization | `src/utils/dom-utils.ts` | Verify DOMPurify and `setTrustedHtml()` behavior against script injection and malicious SVG payloads. | Automated / Manual | **HIGH** |
| **CLIENT-002**| Client-Side | Storage Hygiene | `src/utils/safe-storage.ts` | Verify absence of plaintext API keys or private tokens in `localStorage`/`sessionStorage`. | Automated | **HIGH** |
| **CLIENT-003**| Client-Side | Widget Embed Isolation | `src/utils/widget-sanitizer.ts`, `embed.html` | Test iframe sandbox directives and messaging boundaries for external embedded views. | Manual | **MEDIUM** |
| **WEB-001** | Web Security | HTTP Security Headers | `vercel.json`, `docker/nginx-security-headers.conf` | Verify presence of HSTS, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy. | Automated | **HIGH** |
| **WEB-002** | Web Security | Content Security Policy | `vercel.json` | Verify CSP configuration (`strict-dynamic`, script nonces, frame-ancestors, object-src 'none'). | Automated | **HIGH** |
| **WEB-003** | Web Security | CORS Configuration | `api/_cors.js`, `server/cors.ts` | Test rejection of arbitrary cross-origin requests; ensure first-party and Tauri origin fidelity. | Automated | **HIGH** |
| **TAURI-001** | Native Desktop | IPC Window Gating | `src-tauri/src/main.rs` | Verify that external webview windows (e.g. YouTube login) cannot invoke privileged secret commands. | Manual | **HIGH** |
| **TAURI-002** | Native Desktop | OS Keyring Secrets Vault | `src-tauri/src/main.rs` | Verify that secret read/write operations utilize the native keyring service without unencrypted disk writes. | Manual | **MEDIUM** |
| **TAURI-003** | Native Desktop | External URL Opener | `src-tauri/src/main.rs`, `src-tauri/open-url-safety.test.mjs` | Test validation of external URLs passed to `open_url` command to prevent arbitrary URI scheme execution. | Automated | **HIGH** |
| **CONFIG-001**| Configuration | Frontend Bundle Secrets | `vite.config.ts`, `scripts/check-vite-env-secrets.mjs` | Audit production build artifacts for unstripped environment variables or private API keys. | Automated | **HIGH** |
| **DEP-001** | Dependencies | Dependency Vulnerabilities | `package-lock.json`, `src-tauri/Cargo.lock` | Audit npm, pnpm, and Cargo dependency manifests against known vulnerability advisory databases. | Automated | **MEDIUM** |

---

## Prioritization Summary

- **HIGH Priority Areas (16 tests):**
  Core authentication mechanisms (HMAC session tokens, API keys, sidecar tokens), authorization gates, SSRF defenses (RSS & MCP proxies), DOM/XSS sanitization, HTTP Security Headers & CSP, CORS policies, Tauri IPC window isolation, and build-time secret audits.
- **MEDIUM Priority Areas (8 tests):**
  Enterprise key comparisons, embed token gating, idempotency caching, RPC schema fuzzing, coordinate input boundary handling, widget iframe sandboxing, OS keyring integration, and dependency vulnerability auditing.
- **LOW Priority Areas (1 test):**
  Free-text keyword search and NLP query parameter handling.
- **NOT APPLICABLE:**
  Database injection on client-side (No client-side SQL), OS command injection via web browser (Web runtime has no shell access).
