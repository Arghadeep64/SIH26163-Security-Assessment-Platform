"""Security check CONFIG-001: Information Disclosure in HTTP Responses."""

import re
from datetime import datetime, timezone
from app.scanner.context import ScanContext
from app.scanner.http_client import SafeHttpClient
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, FindingStatus, FindingItem, EvidenceType
from app.scanner.evidence import create_evidence

STACK_TRACE_PATTERNS = [
    re.compile(r"Traceback \(most recent call last\):", re.IGNORECASE),
    re.compile(r"at (?:[a-zA-Z0-9_$.]+\s*\()?[a-zA-Z0-9_\-\\/.]+:\d+:\d+\)?", re.IGNORECASE),
    re.compile(r"NullPointerException|SyntaxError:|ReferenceError:|TypeError:|UnhandledDemoException", re.IGNORECASE),
    re.compile(r"(?:/home/|/var/www/|/app/|/Users/|[C-Z]:\\[a-zA-Z0-9_\\]+)", re.IGNORECASE),
]


async def check_information_disclosure(context: ScanContext) -> CheckResult:
    """Inspect safe public endpoints for accidental leakage of stack traces, internal paths, or debug output."""
    started_at = datetime.now(timezone.utc)
    client = SafeHttpClient(context)

    result = CheckResult(
        check_id="CONFIG-001",
        category="Configuration Security",
        title="Information Disclosure & Debug Leakage Assessment",
        status=CheckStatus.PASS.value,
        severity=SeverityLevel.INFO.value,
        confidence=90.0,
        description="Assesses whether server endpoints leak internal stack traces, filesystem paths, or verbose debug headers in HTTP responses.",
        affected_component="Error Handling & Response Formatting",
        started_at=started_at,
    )

    endpoints_to_test = ["/", "/health", "/api/health", "/api/demo-error", "/non-existent-probe-test-404"]
    disclosures = []

    for path in endpoints_to_test:
        resp = await client.request("GET", path, timeout=3.0)
        if resp.error or resp.status_code == 0:
            if resp.error and ("ConnectTimeout" in resp.error or "ConnectError" in resp.error):
                break
            continue

        # Check for verbose Server and X-Powered-By headers
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}
        powered_by = headers_lower.get("x-powered-by")
        if powered_by:
            disclosures.append(f"X-Powered-By header disclosed: {powered_by} on {path}")

        # Check body for stack traces or internal filesystem paths
        body = resp.body
        for pat in STACK_TRACE_PATTERNS:
            match = pat.search(body)
            if match:
                snippet = body[max(0, match.start() - 40) : min(len(body), match.end() + 40)]
                disclosures.append(f"Pattern matching internal stack trace / path found on {path}: '{snippet.strip()}'")

                result.evidence.append(
                    create_evidence(
                        evidence_type=EvidenceType.HTTP_RESPONSE,
                        title=f"Information Disclosure Match on {path}",
                        description=f"Status {resp.status_code} emitted detailed runtime or path data",
                        response_data=snippet,
                    )
                )
                break

    if disclosures:
        result.status = CheckStatus.FAIL.value
        result.severity = SeverityLevel.LOW.value
        result.description = f"Potential information disclosure observed in responses: {'; '.join(disclosures)}"
        result.recommendation = "Disable verbose error messages in production and suppress the X-Powered-By HTTP response header."

        prefix = context.get_finding_prefix()
        finding_status = FindingStatus.CONFIRMED.value if context.is_demo_target() else FindingStatus.MANUAL_VERIFICATION.value

        result.findings.append(
            FindingItem(
                finding_code="FINDING-CONFIG-001",
                title=f"{prefix}Controlled Information Disclosure in HTTP Response",
                category="Configuration Security",
                severity=SeverityLevel.LOW.value,
                status=finding_status,
                confidence=90.0,
                description=f"{prefix}Target response exposes internal diagnostic details or runtime headers: {'; '.join(disclosures)}.",
                affected_component="Error Handling & Response Formatting",
                impact="Internal paths or server signatures aid adversaries in mapping server architecture and identifying framework versions.",
                reproduction_steps=f"Perform a safe GET request to {context.target_url}/api/demo-error and observe internal file paths / stack trace signatures.",
                remediation="Configure the server to return sanitized generic error messages in non-development environments and remove X-Powered-By headers.",
            )
        )
    else:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = "No internal stack traces, unhandled debug exceptions, or excessive metadata detected."

    result.completed_at = datetime.now(timezone.utc)
    return result
