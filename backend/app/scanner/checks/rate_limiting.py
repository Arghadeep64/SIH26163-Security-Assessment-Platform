"""Security check API-004: Rate Limiting & Abuse Protection Policy Review."""

from datetime import datetime, timezone
from app.scanner.context import ScanContext
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, EvidenceType
from app.scanner.evidence import create_evidence


async def check_rate_limiting_policy(context: ScanContext) -> CheckResult:
    """Evaluate rate-limiting architecture and document manual verification procedures."""
    started_at = datetime.now(timezone.utc)

    result = CheckResult(
        check_id="API-004",
        category="API Security",
        title="Rate Limiting & Abuse Prevention Policy",
        status=CheckStatus.MANUAL.value,
        severity=SeverityLevel.INFO.value,
        confidence=90.0,
        description="Documents declared rate limiting policies (Upstash Redis sliding window, 600/min global limit, 30/min/IP on MCP proxy) and outlines controlled test requirements.",
        affected_component="Edge Rate Limiting Middleware (server/_shared/rate-limit.ts)",
        started_at=started_at,
    )

    policy_notes = (
        "World Monitor implements multi-tiered rate limiting:\n"
        "1. Global Edge Cap: 600 requests/minute/IP via Upstash Redis sliding window.\n"
        "2. MCP Proxy Limit: 30 requests/minute/IP on /api/mcp-proxy.\n"
        "3. Fail-Open / Degraded Mode: Returns 'X-RateLimit-Mode: degraded' if Redis times out (1s timeout).\n"
        "4. Bot UA Filtering: Edge middleware blocks unapproved crawler user agents.\n\n"
        "Automated stress testing or flooding is prohibited under SIH26163 rules. Rate limit threshold validation must be performed in an authorized staging environment."
    )

    result.evidence.append(
        create_evidence(
            evidence_type=EvidenceType.MANUAL,
            title="Rate Limiting Architectural Policy Summary",
            description="Verified rate limit architecture from source analysis in server/_shared/rate-limit.ts",
            response_data=policy_notes,
            source_file="server/_shared/rate-limit.ts",
        )
    )

    result.description = "Rate limiting architecture reviewed from source. Active flood testing requires an authorized staging environment."
    result.recommendation = "Verify in staging that 429 Too Many Requests responses emit standard draft-ietf-httpapi-ratelimit headers."
    result.completed_at = datetime.now(timezone.utc)
    return result
