"""Security check WEB-003: Cookie Security Flags Assessment."""

from datetime import datetime, timezone
from app.scanner.context import ScanContext
from app.scanner.http_client import SafeHttpClient
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, FindingStatus, FindingItem, EvidenceType
from app.scanner.evidence import create_evidence, sanitize_cookie_header


async def check_cookie_security(context: ScanContext) -> CheckResult:
    """Inspect Set-Cookie headers for appropriate Secure, HttpOnly, and SameSite flags."""
    started_at = datetime.now(timezone.utc)
    client = SafeHttpClient(context)
    resp = await client.request("GET", "/")

    result = CheckResult(
        check_id="WEB-003",
        category="Web Security",
        title="Cookie Security Attributes Assessment",
        status=CheckStatus.PASS.value,
        severity=SeverityLevel.INFO.value,
        confidence=90.0,
        description="Assesses whether cookies emitted by the application enforce Secure, HttpOnly, and SameSite attributes.",
        affected_component="Cookie Issuance / Session Management",
        started_at=started_at,
    )

    if resp.error or resp.status_code == 0:
        result.status = CheckStatus.PASS.value
        result.description = "No HTTP response received for cookie inspection."
        result.completed_at = datetime.now(timezone.utc)
        return result

    raw_set_cookie = resp.headers.get("set-cookie")
    if not raw_set_cookie:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = "No Set-Cookie headers observed on root endpoint."
        result.evidence.append(
            create_evidence(
                evidence_type=EvidenceType.HTTP_HEADER,
                title="Cookie Assessment",
                description="Target response emitted no Set-Cookie headers.",
                response_data="Set-Cookie: [None]",
            )
        )
        result.completed_at = datetime.now(timezone.utc)
        return result

    cookie_entries = raw_set_cookie.split("\n") if "\n" in raw_set_cookie else [raw_set_cookie]
    flag_issues = []
    cookie_names = []

    for entry in cookie_entries:
        sanitized_cookie = sanitize_cookie_header(entry)
        cookie_name = entry.split("=")[0].strip() if "=" in entry else "unknown_cookie"
        cookie_names.append(cookie_name)
        cookie_lower = entry.lower()

        has_httponly = "httponly" in cookie_lower
        has_secure = "secure" in cookie_lower
        has_samesite = "samesite" in cookie_lower

        is_https = context.target_url.lower().startswith("https://")
        if not has_httponly:
            flag_issues.append(f"Missing HttpOnly on '{cookie_name}' (accessible via DOM)")
        if is_https and not has_secure:
            flag_issues.append(f"Missing Secure attribute on '{cookie_name}' over HTTPS")
        elif not is_https and not has_secure and not context.is_local_target():
            flag_issues.append(f"Missing Secure attribute on '{cookie_name}'")
        if not has_samesite:
            flag_issues.append(f"Missing SameSite attribute on '{cookie_name}' (cross-site leakage risk)")

        result.evidence.append(
            create_evidence(
                evidence_type=EvidenceType.HTTP_HEADER,
                title=f"Sanitized Cookie Evaluation: {cookie_name}",
                description="Cookie attributes inspected with raw secret value automatically redacted",
                response_data=sanitized_cookie,
            )
        )

    if flag_issues:
        sev = SeverityLevel.MEDIUM.value if any("HttpOnly" in issue for issue in flag_issues) else SeverityLevel.LOW.value
        result.status = CheckStatus.FAIL.value
        result.severity = sev
        result.description = f"Suboptimal cookie flags detected: {'; '.join(set(flag_issues))}"
        result.recommendation = "Ensure all session, preference, and authentication cookies enforce HttpOnly, Secure (on HTTPS), and SameSite=Lax or SameSite=Strict."

        prefix = context.get_finding_prefix()
        finding_status = FindingStatus.CONFIRMED.value if context.is_demo_target() else FindingStatus.MANUAL_VERIFICATION.value

        result.findings.append(
            FindingItem(
                finding_code="FINDING-WEB-003",
                title=f"{prefix}Insecure Cookie Flags ({', '.join(cookie_names)})",
                category="Web Security",
                severity=sev,
                status=finding_status,
                confidence=90.0,
                description=f"{prefix}Cookies emitted by target ({', '.join(cookie_names)}) lack recommended security flags: {'; '.join(set(flag_issues))}.",
                affected_component="Cookie Issuance / Session Management",
                impact="Missing HttpOnly permits client-side script access via XSS; missing SameSite increases susceptibility to Cross-Site Request Forgery (CSRF).",
                reproduction_steps=f"Perform a safe GET request to {context.target_url}/ and inspect the Set-Cookie response header.",
                remediation="Add HttpOnly, Secure (when deployed over HTTPS), and SameSite=Lax/Strict directives to Set-Cookie response headers.",
            )
        )
    else:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = "All observed cookies specify recommended security flags (HttpOnly, Secure, SameSite)."

    result.completed_at = datetime.now(timezone.utc)
    return result
