# SIH26163 Controlled Security Demo Target

## Important Distinction & Disclaimer

> [!WARNING]
> **THIS DEMO TARGET IS NOT WORLD MONITOR.**
>
> This is an independent, deliberately vulnerable **LOCAL** test application used solely to demonstrate and validate the SIH26163 security-assessment platform workflow (Target → Scan → Detect → Collect Evidence → Create Finding → Assign Severity → Store Evidence → Provide Remediation).
>
> **These weaknesses are intentionally created for demonstration and are not findings against World Monitor.**
>
> **DO NOT** claim these findings exist in World Monitor.
> **DO NOT** modify the World Monitor source repository.
> **DO NOT** test the public World Monitor website (`worldmonitor.app`).

---

## 1. Purpose

The Demo Target provides a harmless, isolated local environment for:
1. Validating that security scanner HTTP checks correctly identify common web vulnerabilities.
2. Confirming that technical evidence is collected and sanitized (e.g. cookie redaction).
3. Verifying the database persistence and REST API lifecycle of findings without interacting with external infrastructure.

---

## 2. Server Configuration

- **Host:** `127.0.0.1`
- **Port:** `9000`
- **Base URL:** `http://127.0.0.1:9000`

---

## 3. Run Command

To start the demo target standalone:

```powershell
# From workspace root using project virtual environment:
.\.venv\Scripts\uvicorn.exe main:app --app-dir demo-target --host 127.0.0.1 --port 9000

# Or via Python module execution:
python -m uvicorn main:app --app-dir demo-target --host 127.0.0.1 --port 9000
```

---

## 4. Intentional Weaknesses & Expected Detections

| Weakness # | Category | Affected Endpoint | Description | Expected Check ID | Severity | Remediation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Missing Security Headers | `GET /` | Response omits `Content-Security-Policy`, `X-Content-Type-Options`, and `Referrer-Policy`. | `WEB-001` | `MEDIUM` | Configure standard security headers at the edge reverse proxy / server layer. |
| **2** | Permissive CORS | `GET /api/demo-data` | Permits arbitrary origin reflection alongside `Access-Control-Allow-Credentials: true`. | `WEB-002` | `HIGH` | Restrict `Access-Control-Allow-Origin` to an explicit whitelist of trusted origins and avoid combining wildcard origins with credentials. |
| **3** | Insecure Cookie Flags | `GET /` | Sets synthetic cookie `demo_session=controlled-demo-value` without `HttpOnly`, `Secure`, or `SameSite`. Scanner redacts value. | `WEB-003` | `MEDIUM` | Enforce `HttpOnly`, `Secure` (on HTTPS), and `SameSite=Lax` or `SameSite=Strict` on session cookies. |
| **4** | Information Disclosure | `GET /api/demo-error` | Returns development stack trace exposing synthetic internal file path (`C:\demo\application\example.py`). | `CONFIG-001` | `LOW` | Disable verbose error messages in production; return generic error payloads and log stack traces internally. |

---

## 5. Endpoints Inventory

- `GET /`: Returns root disclaimer banner and sets unhardened demo session cookie.
- `GET /health` & `GET /api/health`: Harmless health check endpoint.
- `GET /api/demo-data`: Returns harmless non-sensitive demo data with permissive CORS headers.
- `GET /api/demo-error`: Returns synthetic error response with simulated internal stack trace for detection testing.
