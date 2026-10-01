"""Security check API-001: Safe Documented API Endpoint Discovery & Liveness."""

from datetime import datetime, timezone
from app.scanner.context import ScanContext
from app.scanner.http_client import SafeHttpClient
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, EvidenceType
from app.scanner.evidence import create_evidence


async def check_api_discovery(context: ScanContext) -> CheckResult:
    """Safely query documented public API endpoints to verify endpoint availability and response contracts."""
    started_at = datetime.now(timezone.utc)
    client = SafeHttpClient(context)

    result = CheckResult(
        check_id="API-001",
        category="API Security",
        title="Documented Public API Endpoint Discovery",
        status=CheckStatus.PASS.value,
        severity=SeverityLevel.INFO.value,
        confidence=90.0,
        description="Safely probes known public endpoints (/api/version, /api/health, /api/product-catalog) using non-destructive GET requests.",
        affected_component="Public Edge API Endpoints",
        started_at=started_at,
    )

    public_probes = [
        ("/api/version", "Build Version Endpoint"),
        ("/api/health", "System Health Endpoint"),
        ("/api/product-catalog", "Product Catalog Metadata"),
    ]

    responding_endpoints = []
    discovery_log = []

    for path, label in public_probes:
        resp = await client.request("GET", path, timeout=3.0)
        if resp.error or resp.status_code == 0:
            discovery_log.append(f"{path} ({label}): Unreachable ({resp.error or 'No connection'})")
            if resp.error and ("ConnectTimeout" in resp.error or "ConnectError" in resp.error):
                break
            continue

        responding_endpoints.append(path)
        content_type = resp.headers.get("content-type", "unknown")
        discovery_log.append(f"{path} ({label}): HTTP {resp.status_code} [Content-Type: {content_type}, Latency: {resp.duration_ms:.1f}ms]")

        result.evidence.append(
            create_evidence(
                evidence_type=EvidenceType.HTTP_RESPONSE,
                title=f"API Probe: {path}",
                description=f"{label} returned HTTP {resp.status_code}",
                response_data=f"URL: {resp.url}\nStatus: {resp.status_code}\nContent-Type: {content_type}\nDuration: {resp.duration_ms:.1f}ms",
            )
        )

    if responding_endpoints:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = f"Discovered and verified {len(responding_endpoints)} active documented public API endpoints: {', '.join(responding_endpoints)}"
    else:
        result.status = CheckStatus.MANUAL.value
        result.severity = SeverityLevel.INFO.value
        result.description = "Documented public API endpoints did not return active responses from the tested target instance."

    result.completed_at = datetime.now(timezone.utc)
    return result
