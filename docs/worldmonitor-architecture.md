# World Monitor: Comprehensive Technical Architecture & Threat Landscape

- **Target Repository:** `https://github.com/koala73/worldmonitor`
- **Analyzed Commit:** `373294b1500c439de885ec86516a5d4c89c4e3b0`
- **Branch:** `main`
- **Application Version:** `2.10.0`
- **Analysis Date:** `2026-09-26`
- **Assessment Scope:** Static Source Code & Architectural Security Mapping (SIH26163)

---

## 1. Project Directory Structure

Inspection of the World Monitor repository reveals a multi-runtime application encompassing a Vite/TypeScript frontend, Vercel Edge Functions, a Sebuf RPC domain server, a Convex real-time persistence layer, a Tauri v2 / Rust desktop shell with an OS Keyring vault, a Node.js local sidecar, and background ingestion relays:

```text
research/worldmonitor/
├── .github/                      # CI/CD workflows, security audits, release pipelines
├── api/                          # Vercel Edge Functions (HTTP & JSON-RPC entrypoints)
│   ├── _*.js / _*.ts             # Shared Edge runtime helpers (auth, cors, crypto, rate-limiting)
│   ├── [domain]/                 # Specialized Edge route handlers (aviation, news, mcp, etc.)
│   ├── bootstrap.js              # Initial dashboard state aggregator
│   ├── mcp-proxy.ts              # Pro-gated Model Context Protocol (MCP) upstream proxy
│   ├── rss-proxy.js              # SSRF-guarded external feed proxy
│   └── wm-session.js             # HMAC-signed anonymous session token issuer
├── blog-site/                    # Astro-based static documentation and blog
├── cli/                          # World Monitor command-line interface tools
├── consumer-prices-core/         # Economic and consumer price indexing engine
├── convex/                       # Convex backend schema, mutations, actions, and Dodo webhooks
│   ├── schema.ts                 # Database schema (users, preferences, API keys, subscriptions)
│   ├── auth.config.ts            # Clerk JWT issuer integration
│   └── http.ts                   # Internal validation routes and external webhook consumers
├── data/                         # Static geospatial, country corpus, and baseline dataset files
├── deploy/                       # Cloud deployment configurations (Vercel, Railway, Umami)
├── docker/                       # Dockerfiles, Nginx security headers, local Redis proxy
├── docs/                         # Developer manuals, API specs, security advisories, OpenAPI schemas
├── proto/                        # Protocol Buffer definitions for Sebuf RPC services
├── scripts/                      # Build helpers, security linters, feed validators, and AIS relays
├── server/                       # Sebuf RPC Domain Gateway and backend service handlers
│   ├── _shared/                  # Gateway auth, rate limiting, entitlements, and SSRF helpers
│   ├── gateway.ts                # Central multi-domain routing & security gateway
│   └── worldmonitor/             # 37+ domain packages (conflict, military, trade, cyber, etc.)
├── shared/                       # Cross-runtime contracts, policies, and attribution riders
├── src/                          # Frontend core (TypeScript, Preact/DOM-based reactive UI)
│   ├── components/               # UI components, modals, and map overlays
│   ├── services/                 # Client-side API clients and state sync
│   ├── utils/                    # dom-utils (DOMPurify/TrustedHtml), safe-storage, encryption
│   └── main.ts                   # Web application entry point and bootstrapping
├── src-tauri/                    # Tauri v2 Desktop application (Rust + Node.js Sidecar)
│   ├── src/main.rs               # Rust backend, IPC command handlers, OS Keyring integration
│   ├── capabilities/             # Tauri v2 fine-grained window capability definitions
│   ├── sidecar/                  # Node.js local API sidecar server (local-api-server.mjs)
│   └── tauri.conf.json           # Desktop security configuration, CSP, and window profiles
└── middleware.ts                 # Edge middleware for UA bot filtering, routing, and variant mapping
```

---

## 2. Technology Inventory

| Technology / Component | Purpose | Relevant Files & Directories | Security Relevance |
| :--- | :--- | :--- | :--- |
| **TypeScript / JavaScript** | Primary codebase language across frontend and backend | `src/`, `api/`, `server/`, `scripts/` | Strict null checking, type safety, runtime boundary validation |
| **Vite 6** | Frontend bundling and dev server | `vite.config.ts`, `package.json` | Bundling budgets, asset isolation, environment variable stripping |
| **Preact / Vanilla DOM** | Lightweight reactive UI rendering | `src/`, `src/utils/dom-utils.ts` | Custom DOM builder (`h()`), `setTrustedHtml()`, `DOMPurify` protection against XSS |
| **Vercel Edge Runtime** | Serverless Edge functions for API endpoints | `api/`, `middleware.ts`, `vercel.json` | Low latency, non-Node Vercel Edge sandbox, IP identification via headers |
| **Sebuf RPC / Protocol Buffers** | Proto-first domain RPC gateway | `proto/`, `server/gateway.ts`, `server/worldmonitor/` | Strict schema validation, typed request deserialization, error wrapping |
| **Tauri v2 & Rust** | Native desktop shell container | `src-tauri/Cargo.toml`, `src-tauri/src/main.rs` | Native security boundary, IPC command isolation, window permission control |
| **OS Keyring (`keyring` crate)** | Consolidated secrets vault | `src-tauri/src/main.rs` | Hardware/OS-backed encrypted credential storage (Keychain / Windows Credential Manager) |
| **Node.js Local Sidecar** | Local desktop API proxy & cache | `src-tauri/sidecar/local-api-server.mjs` | Localhost HTTP server protected by CSPRNG token (`x-worldmonitor-local-token`) |
| **Convex** | Real-time database & user preference sync | `convex/schema.ts`, `convex/http.ts` | Row-level data access, Clerk-authenticated mutations, encrypted config |
| **Clerk** | User authentication provider | `convex/auth.config.ts`, `server/_shared/auth-session.ts` | JWT validation, identity claims, session tokens |
| **Dodo Payments** | Payment processing & subscriptions | `convex/payments/`, `server/_shared/entitlement-check.ts` | Entitlement validation, tier checking, webhook signature verification |
| **Upstash Redis** | Distributed caching & rate limiting | `api/_upstash-json.js`, `server/_shared/rate-limit.ts` | Sliding window rate limits, token buckets, cache invalidation |
| **Web Crypto API** | Cryptographic primitives in Edge & Browser | `api/_crypto.js`, `api/_session.js` | HMAC-SHA256 signatures, constant-time byte comparisons, nonce generation |
| **DOMPurify** | Client-side HTML sanitization | `src/utils/dom-utils.ts`, `package.json` | Strip disallowed HTML elements and malicious attributes |

---

## 3. Application Architecture & Trust Boundaries

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT RUNTIMES                                    │
│                                                                                 │
│   Web Browser (Browser Sandbox)             Tauri v2 Desktop App (Native Shell) │
│   ┌──────────────────────────────┐          ┌────────────────────────────────┐  │
│   │ • DOMPurify / TrustedHtml    │          │ • Rust Core (`main.rs`)        │  │
│   │ • safe-storage (no secrets)  │          │ • OS Keyring (Secrets Vault)   │  │
│   │ • Anonymous `wms_` Token     │          │ • Tauri IPC Origin Gate        │  │
│   └──────────────┬───────────────┘          └───────────────┬────────────────┘  │
└──────────────────┼──────────────────────────────────────────┼───────────────────┘
                   │ HTTPS Request                            │ IPC / Local Token
                   ▼                                          ▼
┌────────────────────────────────────────┐     ┌──────────────────────────────────┐
│          VERCEL EDGE NETWORK           │     │    DESKTOP SIDECAR (LOCAL)       │
│                                        │     │                                  │
│  • Edge Middleware (`middleware.ts`)   │     │  • `local-api-server.mjs`        │
│    - Bot UA Filtering & Rate Limits    │     │  • `x-worldmonitor-local-token`  │
│    - Host Routing & Variant Aliasing   │     │  • IPv4 Socket Pinning           │
│  • Security Headers & Strict CSP       │     │  • Private IP Blocking           │
│  • Edge Endpoints (`/api/*`)           │     └────────────────┬─────────────────┘
└──────────────────┬─────────────────────┘                      │
                   │                                            │
                   ▼                                            │
┌────────────────────────────────────────────────────────┐      │
│                BACKEND SERVICES & ROUTING              │      │
│                                                        │      │
│  • Sebuf Domain Gateway (`server/gateway.ts`)          │◄─────┘
│    - Auth Validation (Session / API Key / Clerk)       │
│    - Entitlement Enforcement (Free / Pro / Enterprise) │
│    - Upstash Redis Rate Limiting                       │
│    - Sub-Request Admission Control                     │
│                                                        │
│  • Specialized Proxies:                                │
│    - `rss-proxy.js`: Domain Allowlist & SSRF Check     │
│    - `mcp-proxy.ts`: Pre-flight DoH DNS & IP Filter    │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ├──► Convex Realtime Backend (User Prefs, Webhooks, API Keys)
                   ├──► Upstash Redis (Distributed Cache & Sliding Rate Limits)
                   ├──► Clerk / Dodo Payments (Identity & Subscription Verification)
                   └──► External OSINT APIs & RSS Feeds (Read-Only Data Ingestion)
```

### Trust Boundaries & Privilege Separation:
1. **Web Client ↔ Edge Gateway**: The browser is completely untrusted. Origin, Referer, and Sec-Fetch headers are treated as client-controlled. Anonymous access requires an HMAC-SHA256 session token (`wms_...`).
2. **Desktop Shell ↔ Sidecar**: Communication between the Tauri webview and the local Node.js sidecar is authenticated via a per-session CSPRNG transport token (`x-worldmonitor-local-token`).
3. **Rust Core ↔ OS Keyring**: API keys and external secrets are stored strictly in the operating system credential manager (`keyring` crate) and never written to unencrypted disk files.
4. **Edge Proxies ↔ External Networks**: All outbound HTTP requests initiated on behalf of clients (RSS feeds, MCP servers, webhooks) pass through explicit SSRF mitigation layers (domain allowlisting, pre-flight DNS address validation, and redirect re-checks).

---

## 4. Authentication Architecture

World Monitor implements a multi-tiered authentication architecture designed for different consumer types:

```text
Authentication Mechanism Flow:

1. Anonymous Web Users:
   Browser -> POST /api/wm-session -> Receives HMAC-signed `wms_<payload>.<sig>` token (12h TTL) -> Sent via HttpOnly cookie or Header.

2. User API Key (Self-Hosted / Pro):
   Client -> Header `X-WorldMonitor-Key: wm_<40_hex>` -> Gateway validates against Convex backend (`/api/internal-validate-api-key`).

3. Enterprise API Key:
   Operator / Partner -> Header `X-WorldMonitor-Key: <key>` -> Gateway validates constant-time against `WORLDMONITOR_VALID_KEYS`.

4. Clerk Authenticated Users:
   Browser / Client -> Header `Authorization: Bearer <clerk_jwt>` -> Gateway verifies claims and user ID.

5. Tauri Desktop Sidecar:
   Tauri Webview -> Header `x-worldmonitor-local-token: <csprng_token>` -> Sidecar verifies session match.
```

- **Credential Storage**: Web sessions store tokens in browser cookies/memory; desktop stores credentials in native OS Keychains; Convex stores hashed API key records.
- **Sensitive Operations**: Secret injection into external requests occurs strictly on server/sidecar runtimes; API keys are never echoed back to clients.

---

## 5. Authorization & Access Control

Access control is enforced at the Gateway and Handler levels using fine-grained entitlement rules:

| Surface / Resource | Required Entitlement | Enforcing Component | Mechanism |
| :--- | :--- | :--- | :--- |
| **Public Dashboard Data** | Free / Anonymous (`wms_` session) | `server/gateway.ts` | Session token validation + baseline rate limits |
| **Pro Data Feeds & Scenarios** | Tier 1 / Pro Subscription | `server/_shared/entitlement-check.ts` | Dodo Payments subscription check in Convex |
| **MCP Proxy (`/api/mcp-proxy`)** | Pro / Enterprise Caller | `api/mcp-proxy.ts` | `resolvePremiumCallerIdentity()`, IP rate limits |
| **Embed Panels (`/api/embed/*`)** | Valid Embed Token | `server/gateway.ts` | `hasEmbedAccess()`, `EMBED_KEY_RPC_PATHS` |
| **Internal RPCs (`/api/internal/*`)** | `RELAY_SHARED_SECRET` | `server/_shared/internal-auth.ts` | Constant-time HMAC-SHA256 signature verification |
| **Tauri IPC Secrets Management** | Trusted Window (`main`, `settings`) | `src-tauri/src/main.rs` | Window label validation (`SECRET_MANAGEMENT_WINDOWS`) |

---

## 6. Server-Side Request Forgery (SSRF) Defenses

World Monitor incorporates multi-stage SSRF defenses across all components making outbound HTTP requests:

1. **RSS Proxy (`api/rss-proxy.js`)**:
   - Matches upstream feed hosts against `api/_rss-allowed-domains.js`.
   - Normalizes hostnames (strips `www.` and tests apex, bare, and full forms).
   - Re-evaluates allowlist match on **every HTTP redirect** up to 3 hops (`MAX_DIRECT_REDIRECTS = 3`).
   - Hard limits payload sizes (`MAX_FEED_BYTES = 5MB`, `MAX_FEED_ITEMS = 20`).

2. **MCP Proxy (`api/mcp-proxy.ts`)**:
   - Enforces `https://` protocol only.
   - Rejects known dangerous hostnames (`localhost`, `169.254.169.254`, `metadata.google.internal`, etc.).
   - Executes pre-flight DNS lookup via Cloudflare DoH (`https://cloudflare-dns.com/dns-query`) and blocks private/reserved IPv4 and IPv6 addresses (`isBlockedResolvedAddress`).
   - Strips cloud metadata request headers.

3. **Desktop Sidecar (`src-tauri/sidecar/local-api-server.mjs`)**:
   - Overrides `globalThis.fetch` to force IPv4 resolution and prevent IPv6 timeout failures.
   - Pins the socket connection directly to the pre-validated IP address (`makePinnedLookup`).

---

## 7. Client-Side Security Controls

1. **DOM Injection Prevention**:
   - Direct `element.innerHTML = ...` is banned across the frontend by repository lint rules (`scripts/enforce-safe-html.mjs`).
   - Dynamic HTML rendering routes through `src/utils/dom-utils.ts` utilizing `setTrustedHtml()`, `safeHtml()`, and `DOMPurify`.
2. **Local Storage Safety**:
   - `scripts/enforce-safe-local-storage.mjs` AST-checks code to prevent direct unhandled `localStorage` dereferences.
   - Sensitive tokens, credentials, and passwords are never persisted to `localStorage` or `sessionStorage`.
3. **Content Security Policy**:
   - Enforces `'strict-dynamic'` script loading with nonces (`nonce-wm-static-bootstrap`) and sha256 hashes.
   - Restricts `object-src 'none'`, `base-uri 'self'`, and restricts iframe framing (`frame-ancestors`).
