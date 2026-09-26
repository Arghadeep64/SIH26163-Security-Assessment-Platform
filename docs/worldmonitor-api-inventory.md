# World Monitor: API Inventory & Endpoint Security Mapping

- **Commit:** `373294b1500c439de885ec86516a5d4c89c4e3b0`
- **Source Inspection:** `api/`, `server/gateway.ts`, `server/worldmonitor/`, `middleware.ts`
- **Analysis Mode:** Static Source Code & Contract Audit

---

## 1. Top-Level Edge Function Endpoints

| Endpoint | Method | Source File | Auth Required | Authorization / Tier | Rate Limit Policy | Security Controls & Features |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`/api/version`** | `GET` | `api/version.js` | None (Public) | None | Public Default | Returns build version and commit hash; bypasses bot gate. |
| **`/api/health`** | `GET` | `api/health.js` | None (Public) | None | Public Default | Service health and upstream dependency status; public monitoring. |
| **`/api/wm-session`** | `POST` | `api/wm-session.js` | None (Public) | None | IP Sliding Window | Mints HMAC-SHA256 session token `wms_...` in HttpOnly cookie. |
| **`/api/bootstrap`** | `GET`, `POST` | `api/bootstrap.js` | Optional | Free / Pro | Global Cap (600/min) | Aggregates initial layers, hot spots, news, and market data. |
| **`/api/rss-proxy`** | `GET` | `api/rss-proxy.js` | Optional / Session | Free / Pro | Scoped IP Limit | Domain allowlist verification; redirect re-check; payload size bound. |
| **`/api/mcp-proxy`** | `POST` | `api/mcp-proxy.ts` | Required | Pro / Enterprise | 30/min/IP | Pre-flight DNS DoH check, private IP blocking, stripped metadata headers. |
| **`/api/mcp`** | `POST` | `api/mcp.ts` | Required | Pro / Enterprise | Endpoint Policy | Model Context Protocol JSON-RPC tool provider. |
| **`/api/create-checkout`**| `POST` | `api/create-checkout.ts`| Optional | Clerk User | IP Throttling | Initiates Dodo Payments checkout sessions. |
| **`/api/customer-portal`**| `POST` | `api/customer-portal.ts`| Required | Clerk User | IP Throttling | Manages customer billing subscriptions via Dodo Payments. |
| **`/api/notify`** | `POST` | `api/notify.ts` | Required | User Auth | User Plan Limit | Triggers user notification alerts across configured channels. |
| **`/api/user-prefs`** | `GET`, `POST` | `api/user-prefs.ts` | Required | Clerk User | User Tier Limit | Syncs user settings, panel layout, and followed entities. |
| **`/api/security/report`**| `POST` | `api/security/report.ts`| None (Public) | None | Scoped Report Cap | COOP/COEP and CSP violation reporting sink. |
| **`/api/seed-contract-probe`**| `GET`| `api/seed-contract-probe.ts`| Required (`RELAY_SHARED_SECRET`)| Internal / Ops | Operator Guard | Probes seeder health and cache contracts; bypasses bot UA filter. |

---

## 2. Sebuf RPC Domain Gateway Endpoints (`server/gateway.ts`)

The Sebuf Domain Gateway routes structured Protocol Buffer RPC requests into 37+ specialized domain subpackages under `server/worldmonitor/`. Each route supports both standard RPC calls and REST projections:

### Domain Categories & Representative RPC Routes:

| Domain | Representative Routes | Auth Mechanism | Upstream Sources / Sinks | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| **Aviation** | `/api/aviation/flights`, `/api/aviation/notams`, `/api/aviation/military` | Session / API Key | OpenSky Network, FAA NOTAMs, ADS-B Exchange | 120/min/IP |
| **Conflict & Geopolitics** | `/api/conflict/events`, `/api/conflict/hotspots`, `/api/conflict/summary` | Session / API Key | ACLED, UCDP, Liveuamap feeds | 60/min/IP |
| **Cyber Intelligence** | `/api/cyber/threats`, `/api/cyber/indicators`, `/api/cyber/incidents` | Session / API Key | OTX, AbuseIPDB, CISA Advisories | 60/min/IP |
| **Displacement & Migration**| `/api/displacement/trends`, `/api/displacement/corridors` | Session / API Key | UNHCR, IOM, HDX datasets | 60/min/IP |
| **Economic & Trade** | `/api/economic/indicators`, `/api/trade/chokepoints`, `/api/trade/tariffs` | Session / API Key | FRED, World Bank, WTO, IMF | 60/min/IP |
| **Energy & Commodities** | `/api/energy/grid`, `/api/energy/outages`, `/api/market/quotes` | Session / API Key | EIA, Finnhub, Yahoo Finance, Alpha Vantage | 120/min/IP |
| **Natural Disasters & Space** | `/api/natural/earthquakes`, `/api/wildfire/hotspots`, `/api/radiation/sensors` | Session / API Key | USGS, NASA FIRMS, Safecast | 120/min/IP |
| **News & Intelligence** | `/api/news/headlines`, `/api/intelligence/briefs`, `/api/intelligence/analysis` | Session / API Key | RSS Aggegator, Telegram Relays, LLM Providers | 60/min/IP |
| **Scenario & Predictions** | `/api/scenario/evaluate`, `/api/prediction/markets` | Pro / Enterprise Tier | Polymarket, Kalshi, Internal Scenario Engine | 30/min/IP |
| **Webcams & Live Imagery** | `/api/webcam/streams`, `/api/imagery/satellite` | Session / Embed Key | Windy Webcams, Sentinel, Planet Labs | 120/min/IP |

---

## 3. Internal & Privileged API Endpoints

| Endpoint | Method | Source Location | Security & Auth Requirements | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`/api/internal/brief-why-matters`** | `POST` | `server/_shared/internal-auth.ts` | `RELAY_SHARED_SECRET` (Bearer Header via WebCrypto HMAC) | Background notification summary generator for cron jobs. |
| **`/api/internal-validate-api-key`** | `POST` | `convex/http.ts` | `CONVEX_SERVER_SHARED_SECRET` | Backend verification of user API key validity and scopes. |
| **`/api/internal-entitlements`** | `POST` | `convex/http.ts` | `CONVEX_SERVER_SHARED_SECRET` | Resolves user plan tier, active subscription, and limits. |
| **`/api/cache-purge`** | `POST` | `api/cache-purge.js` | Operator Enterprise Key | Purges distributed Redis and edge CDN cache keys. |

---

## 4. Desktop Sidecar API Endpoints (`src-tauri/sidecar/local-api-server.mjs`)

| Local Path | Method | Auth Requirement | Security Controls |
| :--- | :--- | :--- | :--- |
| **`http://127.0.0.1:46123/api/*`** | All | `x-worldmonitor-local-token` | Local loopback binding only; CSPRNG token validation; IPv4 fetch override with socket pinning. |
| **`http://127.0.0.1:46123/logs`** | `GET` | `x-worldmonitor-local-token` | Sanitized local sidecar execution and diagnostic logs. |
| **`http://127.0.0.1:46123/health`** | `GET` | `x-worldmonitor-local-token` | Local process liveness and provider credential availability. |
