# World Monitor: Documented Security Baseline & Threat Context

- **Source Commit:** `373294b1500c439de885ec86516a5d4c89c4e3b0`
- **Official Policy Reference:** `research/worldmonitor/SECURITY.md`
- **Advisory References:** `research/worldmonitor/docs/security/`, GitHub Security Advisories

---

## 1. Documented Security Controls & Policies

Based on the target application's `SECURITY.md` and architecture documentation, the following security controls are actively maintained by the upstream project:

1. **API Keys & Secret Storage**:
   - Web: Secrets are maintained strictly in server-side Vercel Edge Function environment variables.
   - Desktop (Tauri): Secrets are managed via the OS Keyring (`keyring` crate) in a consolidated vault entry; plaintext on-disk storage is explicitly banned.
   - Repositories: Strict CI linters (`scripts/check-local-secret-dumps.mjs`, `scripts/check-vite-env-secrets.mjs`) block accidental commits of `.env` files or exposed client secrets.

2. **Network & Proxy Defenses**:
   - **SSRF Mitigation**: The RSS proxy utilizes strict domain allowlisting (`api/_rss-allowed-domains.js`) and re-verifies the allowlist across every redirect hop.
   - **MCP Proxy Protection**: Accepts only HTTPS URLs, queries Cloudflare DoH to resolve IP addresses before connecting, drops requests resolving to private/reserved ranges, and removes cloud-metadata headers.

3. **Client-Side Protections**:
   - **DOM Sanitization**: HTML from external feeds and user inputs is processed via `DOMPurify` and custom `TrustedHtml` wrappers in `src/utils/dom-utils.ts`.
   - **Content Security Policy**: Implements `'strict-dynamic'` script sourcing, disables `unsafe-eval` (except controlled wasm), and restricts object and frame embedding.
   - **Storage Hygiene**: Direct unhandled `localStorage` access is blocked to prevent Android WebView `TypeError` crashes and token leaks.

4. **Desktop & Tauri Sandboxing**:
   - **IPC Window Gating**: Sensitive IPC commands (secrets management, cache modifications) are restricted to trusted windows (`main`, `settings`).
   - **Sidecar Authentication**: A per-session CSPRNG token (`x-worldmonitor-local-token`) is required for every request reaching the local sidecar.
   - **DevTools**: Explicitly compiled out of release builds.

---

## 2. In-Scope vs. Out-of-Scope Security Areas

### In-Scope:
- Vulnerabilities within Edge Functions and Sebuf RPC Handlers (SSRF, parameter injection, auth bypass).
- Cross-Site Scripting (XSS) or HTML injection via external feeds, maps, or user-controlled queries.
- Secret leakage or API key exposure in frontend bundles or build artifacts.
- Tauri IPC command privilege escalation or window capability bypasses.
- Sidecar transport token leakage or local loopback authentication bypasses.
- Dependency vulnerabilities with verifiable execution paths in production.

### Out-of-Scope:
- Upstream third-party service vulnerabilities (OSINT providers, external APIs).
- Social engineering attacks against operators.
- Denial of Service (DoS) / Distributed Denial of Service (DDoS) against cloud infrastructure.
- Insecure configurations manually provisioned by self-hosting users.

---

## 3. Previously Disclosed Security Context (Baseline History)

*Note: The following items are documented baseline findings from repository history and public advisories. They represent architectural context rather than new discoveries.*

1. **Resolve-vs-Connect DNS Rebinding Window (Draft Advisory `GHSA-887j-p88r-qmm9`)**:
   - *Context:* Vercel Edge `fetch()` validates IP addresses via DoH prior to connection, but cannot pin its underlying socket to the vetted address. A narrow resolve-vs-connect DNS rebinding window remains an acknowledged architectural limitation of edge runtimes until Node-runtime socket pinning is adopted.
2. **Referer / Origin Trust Bypass (Issue `#3541`)**:
   - *Context:* Earlier versions relied on `Origin` / `Referer` headers to verify "trusted browser" callers. These headers were forgeable by raw sockets/curl. The project resolved this by introducing HMAC-signed `wms_` session tokens minted via `POST /api/wm-session`.
3. **Android WebView `localStorage` Crash Bug (`#7833`)**:
   - *Context:* WebViews with DOM storage disabled exposed `localStorage` as null, triggering unhandled `TypeError` exceptions. The project added AST linters and `safe-storage.ts` to enforce guarded access.
4. **Dependency Advisories (Documented in `docs/security/dependency-dispositions-2026-09-08.md`)**:
   - *Context:* The repository maintains active audit trails evaluating transitive npm/pnpm and Cargo dependencies (such as `image-size`, `stream-json`, `uuid`, `astro`), documenting that inactive sub-paths or non-hydrated templates mitigate theoretical risk.
