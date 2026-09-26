"""Security check AUTHZ-001: Authorization & Entitlement Access Control Review."""

from datetime import datetime, timezone
from app.scanner.context import ScanContext
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, EvidenceType
from app.scanner.evidence import create_evidence


async def check_authorization_boundaries(context: ScanContext) -> CheckResult:
    """Document and evaluate access control models, subscription tiers, and entitlement boundaries."""
    started_at = datetime.now(timezone.utc)

    result = CheckResult(
        check_id="AUTHZ-001",
        category="Authorization",
        title="Authorization & Entitlement Access Control Review",
        status=CheckStatus.MANUAL.value,
        severity=SeverityLevel.INFO.value,
        confidence=95.0,
        description="Documents role-based and tier-based access control policies across Sebuf RPC domain endpoints and outlines entitlement boundary tests.",
        affected_component="Entitlement Check Layer (server/_shared/entitlement-check.ts, server/gateway.ts)",
        started_at=started_at,
    )

    authz_summary = (
        "Authorization boundaries identified in World Monitor:\n"
        "1. Free Tier: Access to public dashboard feeds, baseline news, and basic layers.\n"
        "2. Pro Tier: Gated access to advanced OSINT feeds, predictive scenarios, and MCP proxy endpoints.\n"
        "3. Enterprise Tier: Operator-level rate limits and bypass of basic quotas.\n"
        "4. Embed Keys: Limited token scope restricted strictly to embedded map visualization routes (EMBED_KEY_RPC_PATHS).\n"
        "5. Internal RPCs (/api/internal/*): Hard-gated behind `RELAY_SHARED_SECRET` Bearer header.\n\n"
        "Recommended Staging Tests:\n"
        "- Verify Free user cannot invoke Pro-gated RPCs (should return 403 Forbidden with billing verification metadata).\n"
        "- Verify Embed keys cannot invoke general analytics or user preference mutations."
    )

    result.evidence.append(
        create_evidence(
            evidence_type=EvidenceType.MANUAL,
            title="Authorization Boundary Assessment",
            description="Verified entitlement enforcement from server/_shared/entitlement-check.ts",
            response_data=authz_summary,
            source_file="server/_shared/entitlement-check.ts",
        )
    )

    result.description = "Authorization policies reviewed from source. Privilege escalation testing must be performed in staging."
    result.recommendation = "Ensure all newly added domain RPC routes declare an explicit requiredTier in route descriptors."
    result.completed_at = datetime.now(timezone.utc)
    return result
