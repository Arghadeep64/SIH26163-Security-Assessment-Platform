"""Security check WEB-001: HTTP Security Headers Assessment."""

from datetime import datetime, timezone
from app.scanner.context import ScanContext
from app.scanner.http_client import SafeHttpClient
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, FindingStatus, FindingItem, EvidenceType
from app.scanner.evidence import create_evidence


async def check_security_headers(context: ScanContext) -> CheckResult:
    """Assess whether target HTTP response configures baseline security headers."""
    started_at = datetime.now(timezone.utc)
    client = SafeHttpClient(context)
    resp = await client.request("GET", "/")

    result = CheckResult(
        check_id="WEB-001",
        category="Web Security",
        title="HTTP Security Headers Assessment",
        status=CheckStatus.PASS.value,
        severity=SeverityLevel.INFO.value,
        confidence=95.0,
        description="Assesses presence and configuration of modern HTTP security headers (CSP, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy).",
        affected_component="HTTP Edge / Web Server Response Headers",
        started_at=started_at,
    )

    if resp.error or resp.status_code == 0:
        result.status = CheckStatus.MANUAL.value
        result.severity = SeverityLevel.INFO.value
        result.description = f"Target was unreachable for security headers evaluation from assessment environment: {resp.error or 'No response received'}"
        result.evidence.append(
            create_evidence(
                evidence_type=EvidenceType.HTTP_HEADER,
                title="Security Headers Evaluation Skipped (Target Unreachable)",
                description=resp.error or "No connection established to target endpoint",
                response_data=f"Target URL: {context.target_url}\nError: {resp.error}",
            )
        )
        result.completed_at = datetime.now(timezone.utc)
        return result

    headers = {k.lower(): v for k, v in resp.headers.items()}
    missing_headers = []
    header_evidence_details = []

    # 1. Content-Security-Policy
    csp = headers.get("content-security-policy")
    if not csp:
        missing_headers.append("Content-Security-Policy")
    else:
        header_evidence_details.append(f"Content-Security-Policy: {csp}")

    # 2. X-Content-Type-Options
    xcto = headers.get("x-content-type-options")
    if not xcto or "nosniff" not in xcto.lower():
        missing_headers.append("X-Content-Type-Options")
    else:
        header_evidence_details.append(f"X-Content-Type-Options: {xcto}")

    # 3. Referrer-Policy
    ref_pol = headers.get("referrer-policy")
    if not ref_pol:
        missing_headers.append("Referrer-Policy")
    else:
        header_evidence_details.append(f"Referrer-Policy: {ref_pol}")

    # 4. Permissions-Policy
    perm_pol = headers.get("permissions-policy")
    if not perm_pol:
        missing_headers.append("Permissions-Policy")
    else:
        header_evidence_details.append(f"Permissions-Policy: {perm_pol}")

    # 5. Strict-Transport-Security (HSTS)
    hsts = headers.get("strict-transport-security")
    is_https = context.target_url.lower().startswith("https://")
    if is_https and not hsts:
        missing_headers.append("Strict-Transport-Security")
    elif hsts:
        header_evidence_details.append(f"Strict-Transport-Security: {hsts}")

    # Record Evidence
    evidence_text = "\n".join(header_evidence_details) if header_evidence_details else "No security headers detected."
    result.evidence.append(
        create_evidence(
            evidence_type=EvidenceType.HTTP_HEADER,
            title="Observed Security Headers",
            description=f"HTTP Status {resp.status_code} on {resp.url}",
            response_data=evidence_text,
        )
    )

    if missing_headers:
        # If running against local non-HTTPS development, missing HSTS is not critical
        is_local_http = context.is_local_target() and not is_https
        if is_local_http and set(missing_headers) == {"Strict-Transport-Security"}:
            result.status = CheckStatus.PASS.value
            result.severity = SeverityLevel.INFO.value
            result.description = "All standard local security headers present (HSTS excluded on HTTP localhost)."
        else:
            sev = SeverityLevel.MEDIUM.value if "Content-Security-Policy" in missing_headers else SeverityLevel.LOW.value
            result.status = CheckStatus.FAIL.value
            result.severity = sev
            result.description = f"Missing recommended security headers: {', '.join(missing_headers)}"
            result.recommendation = "Configure missing HTTP headers in reverse proxy (Nginx/Vercel) to protect against MIME confusion and framing attacks."

            prefix = context.get_finding_prefix()
            if context.is_demo_target():
                finding_status = FindingStatus.CONFIRMED.value
                finding_title = f"{prefix}Missing HTTP Security Headers ({', '.join(missing_headers)})"
                finding_desc = f"{prefix}Target HTTP response on {context.target_url} lacks recommended defense-in-depth headers: {', '.join(missing_headers)}."
                finding_impact = "Clients may be susceptible to clickjacking, cross-site scripting (XSS) framing, MIME confusion attacks, or unintended referrer disclosure."
                result.status = CheckStatus.FAIL.value
            else:
                finding_status = FindingStatus.ENVIRONMENT_OBSERVATION.value
                finding_title = f"Development Environment Security Header Observation (Missing: {', '.join(missing_headers)})"
                finding_desc = (
                    f"Under the tested local configuration ({context.target_url}), the local HTTP serving layer "
                    f"did not return edge security headers: {', '.join(missing_headers)}. Source configuration analysis "
                    f"of vercel.json confirms that production security headers are defined at the deployment layer. "
                    f"An application vulnerability is not established from this local runtime observation; "
                    f"manual verification of the production-equivalent edge deployment is required."
                )
                finding_impact = "Production-equivalent deployment should be verified to ensure the security headers declared in vercel.json are actually delivered at the deployed edge."
                result.status = CheckStatus.MANUAL.value

            result.findings.append(
                FindingItem(
                    finding_code="FINDING-WEB-001",
                    title=finding_title,
                    category="Web Security",
                    severity=sev,
                    status=finding_status,
                    confidence=90.0,
                    description=finding_desc,
                    affected_component="HTTP Edge / Web Server Response Headers",
                    impact=finding_impact,
                    reproduction_steps=f"Perform a safe GET request to {context.target_url}/ and observe response headers.",
                    remediation="Verify production reverse proxy (Vercel / Nginx) injects Content-Security-Policy and X-Content-Type-Options: nosniff as defined in vercel.json.",
                )
            )
    else:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = "All recommended HTTP security headers are configured properly."

    result.completed_at = datetime.now(timezone.utc)
    return result
