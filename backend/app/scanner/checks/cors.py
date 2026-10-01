"""Security check WEB-002: Cross-Origin Resource Sharing (CORS) Policy Assessment."""

from datetime import datetime, timezone
from app.scanner.context import ScanContext
from app.scanner.http_client import SafeHttpClient
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, FindingStatus, FindingItem, EvidenceType
from app.scanner.evidence import create_evidence


async def check_cors_policy(context: ScanContext) -> CheckResult:
    """Assess whether target's CORS configuration permits insecure cross-origin sharing."""
    started_at = datetime.now(timezone.utc)
    client = SafeHttpClient(context)

    result = CheckResult(
        check_id="WEB-002",
        category="Web Security",
        title="CORS Policy Security Assessment",
        status=CheckStatus.PASS.value,
        severity=SeverityLevel.INFO.value,
        confidence=90.0,
        description="Assesses Cross-Origin Resource Sharing (CORS) preflight and origin response headers for permissive or insecure configurations.",
        affected_component="CORS Middleware / Origin Validation",
        started_at=started_at,
    )

    test_origins = [
        ("https://unauthorized-third-party.example.com", "Arbitrary Third-Party Origin"),
        ("tauri://localhost", "Tauri Desktop Loopback Origin"),
        ("https://app.worldmonitor.app", "First-Party App Origin"),
    ]

    target_paths = ["/api/demo-data", "/api/health", "/"]

    findings_notes = []
    has_unsafe_cors = False

    for test_origin, label in test_origins:
        resp = None
        # Probe candidate paths
        for path in target_paths:
            resp = await client.request(
                method="OPTIONS",
                path=path,
                headers={
                    "Origin": test_origin,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization, Content-Type",
                },
                timeout=3.0,
            )
            if not resp.error and resp.status_code not in (0, 404):
                break
            if resp.error and ("ConnectTimeout" in resp.error or "ConnectError" in resp.error):
                break

            # Fallback to GET
            resp = await client.request(
                method="GET",
                path=path,
                headers={"Origin": test_origin},
                timeout=3.0,
            )
            if not resp.error and resp.status_code not in (0, 404):
                break
            if resp.error and ("ConnectTimeout" in resp.error or "ConnectError" in resp.error):
                break

        if not resp or resp.error:
            continue

        acao = resp.headers.get("access-control-allow-origin")
        acac = resp.headers.get("access-control-allow-credentials", "").lower() == "true"

        evidence_payload = (
            f"Tested Origin: {test_origin} ({label})\n"
            f"Target Path: {resp.url}\n"
            f"Response Status: {resp.status_code}\n"
            f"Access-Control-Allow-Origin: {acao or '[Not Emitted]'}\n"
            f"Access-Control-Allow-Credentials: {resp.headers.get('access-control-allow-credentials', '[Not Emitted]')}\n"
            f"Access-Control-Allow-Methods: {resp.headers.get('access-control-allow-methods', '[Not Emitted]')}"
        )

        result.evidence.append(
            create_evidence(
                evidence_type=EvidenceType.HTTP_HEADER,
                title=f"CORS Preflight Evaluation ({label})",
                description=f"Status {resp.status_code} for origin {test_origin}",
                response_data=evidence_payload,
            )
        )

        # Unsafe case 1: Wildcard origin with credentials
        if (acao == "*" or acao == "null") and acac:
            has_unsafe_cors = True
            findings_notes.append("Wildcard '*' Access-Control-Allow-Origin configured alongside Allow-Credentials: true.")

        # Unsafe case 2: Reflection of arbitrary untrusted third-party origin with credentials
        if acao == test_origin and "unauthorized-third-party" in test_origin and acac:
            has_unsafe_cors = True
            findings_notes.append("Arbitrary third-party origin reflected alongside Allow-Credentials: true.")

    if has_unsafe_cors:
        result.status = CheckStatus.FAIL.value
        result.severity = SeverityLevel.HIGH.value
        result.description = f"Potentially insecure CORS policy detected: {'; '.join(findings_notes)}"
        result.recommendation = "Restrict Access-Control-Allow-Origin to an explicit allowlist of first-party and desktop origins."

        prefix = context.get_finding_prefix()
        finding_status = FindingStatus.CONFIRMED.value if context.is_demo_target() else FindingStatus.MANUAL_VERIFICATION.value

        result.findings.append(
            FindingItem(
                finding_code="FINDING-WEB-002",
                title=f"{prefix}Permissive Cross-Origin Resource Sharing (CORS) Policy",
                category="Web Security",
                severity=SeverityLevel.HIGH.value,
                status=finding_status,
                confidence=90.0,
                description=f"{prefix}Target CORS configuration dynamically reflects arbitrary untrusted origins or allows credentials with wildcard origins: {'; '.join(findings_notes)}.",
                affected_component="CORS Middleware / Origin Validation",
                impact="Untrusted third-party websites visited in a victim's browser could read authenticated cross-origin response data if credentials are transmitted.",
                reproduction_steps=f"Send an OPTIONS/GET request to {context.target_url}/api/demo-data with 'Origin: https://unauthorized-third-party.example.com' and verify Access-Control-Allow-Origin and Access-Control-Allow-Credentials headers.",
                remediation="Configure an explicit allowlist of origins and ensure credentials are never permitted when matching arbitrary untrusted origins.",
            )
        )
    else:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = "CORS policy properly restricts origins and credentials."

    result.completed_at = datetime.now(timezone.utc)
    return result
