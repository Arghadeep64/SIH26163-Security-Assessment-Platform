# World Monitor Local Runtime & Serving Layer Analysis

## 1. Executive Summary

This document records the architectural analysis of the local serving and runtime environment for the **World Monitor** application ([commit `373294b1500c439de885ec86516a5d4c89c4e3b0`](file:///c:/Visual%20Studio%20code/SIH26163/research/worldmonitor)).

During the Phase 8 security assessment (Assessment ID `200`), automated scanning against `http://127.0.0.1:3000` observed that the local HTTP response did not contain modern production security headers (`Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`), resulting in `FINDING-WEB-001`. The response header identified the server banner as `Server: SimpleHTTP/0.6 Python/3.12.10`.

This review investigates the local runtime layer to establish whether the observed behavior represents an application vulnerability or an environment-specific development configuration.

---

## 2. Local Runtime & Serving Architecture

### 2.1 Process & Serving Layer
1. **Repository Development Configuration:**
   - Documented startup command: `npm run dev` (running `vite` on port 3000).
   - Vite is configured in [`research/worldmonitor/vite.config.ts`](file:///c:/Visual%20Studio%20code/SIH26163/research/worldmonitor/vite.config.ts) to serve the SPA client bundle (`index.html`, `/src`, `/public`) with hot module reloading.
2. **Local Assessment Wrapper (`research/run_local_worldmonitor.py`):**
   - For isolated, non-destructive automated scanning within the testbed, a local lightweight HTTP daemon is executed on `http://127.0.0.1:3000`.
   - It directly serves the static assets (`index.html`, `/public`, `/api/version`, `/api/health`, `/api/product-catalog`) from the cloned repository using Python's standard `http.server`.
   - **Critical Finding:** The HTTP response inspected during automated scanning was produced by this local development serving layer, not by an edge reverse proxy.

---

## 3. Security Header Comparison: Local vs Production

| Security Header | Local Dev / Wrapper Response (`127.0.0.1:3000`) | Production Specification ([`research/worldmonitor/vercel.json`](file:///c:/Visual%20Studio%20code/SIH26163/research/worldmonitor/vercel.json)) |
|---|---|---|
| **`Content-Security-Policy`** | *Omitted* (Standard local dev behavior) | Configured at edge and sandbox routes (`/wm-widget-sandbox.html`) |
| **`Strict-Transport-Security`** | *Omitted* (HTTP loopback) | Enforced in Vercel production edge |
| **`X-Content-Type-Options`** | *Omitted* by local server | Injected by production reverse proxy |
| **`Referrer-Policy`** | *Omitted* by local server | Enforced in edge deployment |
| **`Cache-Control`** | Standard HTTP headers | Comprehensive policy in `vercel.json` (lines 850–928) |

---

## 4. Source Security Controls & Mitigations

### 4.1 DOM Insertion & XSS (`innerHTML`, `dangerouslySetInnerHTML`)
- **Observation:** Static regex scanning in `SOURCE-001` identified usages of DOM manipulation patterns across the repository.
- **Source Audit & Verified Controls:**
  1. [`research/worldmonitor/scripts/enforce-safe-html.mjs`](file:///c:/Visual%20Studio%20code/SIH26163/research/worldmonitor/scripts/enforce-safe-html.mjs): CI linter that fails the build if raw `innerHTML` or `insertAdjacentHTML` are assigned outside `src/utils/dom-utils.ts`.
  2. All dynamic client-side HTML insertions route through `setTrustedHtml()` which executes **DOMPurify** sanitization.
  3. [`research/worldmonitor/scripts/enforce-safe-local-storage.mjs`](file:///c:/Visual%20Studio%20code/SIH26163/research/worldmonitor/scripts/enforce-safe-local-storage.mjs): Protects sensitive local storage keys.

### 4.2 Subprocess Execution (`child_process`)
- **Observation:** `child_process` imports detected in repository search.
- **Source Audit & Verified Controls:**
  1. All `child_process` invocations are confined to build scripts ([`scripts/bundle-runner.js`](file:///c:/Visual%20Studio%20code/SIH26163/research/worldmonitor/scripts), [`scripts/check-build-prereqs.mjs`](file:///c:/Visual%20Studio%20code/SIH26163/research/worldmonitor/scripts)) and offline unit tests ([`tests/`](file:///c:/Visual%20Studio%20code/SIH26163/research/worldmonitor/tests)).
  2. Browser bundles use [`src/shims/child-process.ts`](file:///c:/Visual%20Studio%20code/SIH26163/research/worldmonitor/src/shims/child-process.ts), which throws an error if called client-side.
  3. No untrusted HTTP request parameters reach any `child_process.exec()` or `spawn()` sink.

---

## 5. Classification Correction Matrix

| Check ID | Original Classification | Corrected Classification | Justification |
|---|---|---|---|
| **`WEB-001`** | `FAIL` / `MEDIUM` (Flagged as potential vulnerability) | **`ENVIRONMENT_OBSERVATION` / `MANUAL_VERIFICATION`** | Missing headers are an artifact of the local development HTTP serving layer; production edge headers are specified in `vercel.json`. An application-level vulnerability is **not established**. |
| **`SOURCE-001`** | `MANUAL` / `LOW` | **`SOURCE_REVIEW` / `INFORMATIONAL`** | Sinks are strictly protected by CI linters (`enforce-safe-html.mjs`) and DOMPurify; `child_process` is offline tooling only. |
| **`API-004`** | `MANUAL` | **`MANUAL_VERIFICATION`** | Rate limiting policies exist in source (`api/_rate-limit.js`) but require Upstash Redis for runtime validation. |
| **`AUTH-001`** | `MANUAL` | **`MANUAL_VERIFICATION`** | Clerk authentication and session signing verified in source; live auth flows require staging credentials. |
| **`AUTHZ-001`** | `MANUAL` | **`MANUAL_VERIFICATION`** | Tier crosswalk and billing checks verified in source; live entitlement gating requires active customer session. |

---

## 6. Technical Limitations of Local Assessment

1. **Edge Proxy Isolation:** Cloud headers (Vercel edge middleware, HSTS, WAF rules) are not active on local loopback (`127.0.0.1:3000`).
2. **Third-Party Services:** Live Redis, Clerk, Stripe, and external intelligence feeds are intentionally not connected during defensive local testing.
3. **Scope Guarantee:** Assessment strictly evaluates the authorized local cloned repository and emits no external network traffic to `worldmonitor.app`.
