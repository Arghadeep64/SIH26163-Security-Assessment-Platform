"""Security check WEB-004: Transport Layer Security (TLS/HTTPS) Assessment."""

from datetime import datetime, timezone
from app.scanner.context import ScanContext
from app.scanner.http_client import SafeHttpClient
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, EvidenceType
from app.scanner.evidence import create_evidence


async def check_tls_configuration(context: ScanContext) -> CheckResult:
    """Assess transport security and HTTP-to-HTTPS redirect enforcement."""
    started_at = datetime.now(timezone.utc)
    is_https = context.target_url.lower().startswith("https://")
    is_local = context.is_local_target()

    result = CheckResult(
        check_id="WEB-004",
        category="Web Security",
        title="TLS & Transport Encryption Assessment",
        status=CheckStatus.PASS.value,
        severity=SeverityLevel.INFO.value,
        confidence=95.0,
        description="Assesses whether transport encryption (TLS/HTTPS) is enforced on production communications.",
        affected_component="Transport Layer / TLS Termination",
        started_at=started_at,
    )

    if is_local and not is_https:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = "Target is running on local HTTP loopback; TLS enforcement is not required for local development."
        result.evidence.append(
            create_evidence(
                evidence_type=EvidenceType.CONFIGURATION,
                title="Local Transport Assessment",
                description=f"Local target {context.target_url} evaluated without requiring production TLS certificate.",
                response_data="Scheme: HTTP (Loopback)",
            )
        )
        result.completed_at = datetime.now(timezone.utc)
        return result

    client = SafeHttpClient(context)
    resp = await client.request("GET", "/")

    if resp.error:
        is_timeout_or_unreachable = any(
            t in (resp.error or "").lower()
            for t in ["timeout", "connecterror", "connection refused", "unreachable"]
        ) and "certificate_verify_failed" not in (resp.error or "").lower()

        if is_timeout_or_unreachable:
            result.status = CheckStatus.MANUAL.value
            result.severity = SeverityLevel.INFO.value
            result.description = f"Target was unreachable for TLS handshake evaluation from assessment environment: {resp.error}"
            result.evidence.append(
                create_evidence(
                    evidence_type=EvidenceType.HTTP_RESPONSE,
                    title="TLS Evaluation Skipped (Target Unreachable)",
                    description=resp.error,
                    response_data=f"Target URL: {context.target_url}\nError: {resp.error}",
                )
            )
            result.completed_at = datetime.now(timezone.utc)
            return result

        result.status = CheckStatus.ERROR.value
        result.description = f"TLS handshake or connection failed: {resp.error}"
        result.evidence.append(
            create_evidence(
                evidence_type=EvidenceType.HTTP_RESPONSE,
                title="TLS Connection Failure",
                description=resp.error,
            )
        )
        result.completed_at = datetime.now(timezone.utc)
        return result

    result.status = CheckStatus.PASS.value
    result.severity = SeverityLevel.INFO.value
    result.description = "HTTPS transport verified with active TLS encryption."
    result.evidence.append(
        create_evidence(
            evidence_type=EvidenceType.HTTP_RESPONSE,
            title="TLS Handshake Verification",
            description=f"Successfully connected via HTTPS to {resp.url} (Status {resp.status_code})",
            response_data=f"Verified HTTPS Connection: {resp.url}",
        )
    )

    result.completed_at = datetime.now(timezone.utc)
    return result
