"""Security check AUTH-001: Authentication & Session Management Architecture Review."""

from datetime import datetime, timezone
from app.scanner.context import ScanContext
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, EvidenceType
from app.scanner.evidence import create_evidence


async def check_authentication_architecture(context: ScanContext) -> CheckResult:
    """Document and assess authentication mechanisms and manual verification procedures."""
    started_at = datetime.now(timezone.utc)

    result = CheckResult(
        check_id="AUTH-001",
        category="Authentication",
        title="Authentication & Session Management Architecture",
        status=CheckStatus.MANUAL.value,
        severity=SeverityLevel.INFO.value,
        confidence=95.0,
        description="Analyzes authentication mechanisms from source and outlines manual verification test cases for anonymous, user, and enterprise identities.",
        affected_component="Authentication Layer (api/_session.js, api/_user-api-key.js, api/_api-key.js)",
        started_at=started_at,
    )

    auth_architecture_summary = (
        "Authentication mechanisms identified in World Monitor:\n"
        "1. Anonymous Browser Sessions: HMAC-SHA256 tokens (`wms_<payload>.<sig>`, 12h TTL) issued via POST /api/wm-session using Web Crypto API.\n"
        "2. User API Keys: `wm_<40_hex>` validated against Convex database (/api/internal-validate-api-key) and cached for 60s in Redis.\n"
        "3. Enterprise Keys: Server-side environment variable `WORLDMONITOR_VALID_KEYS` verified with timingSafeIncludes.\n"
        "4. User Account Sessions: Clerk JWT validation in Convex (auth.config.ts) and server/_shared/auth-session.ts.\n"
        "5. Desktop Sidecar: CSPRNG transport token (`x-worldmonitor-local-token`) passed between webview and Node.js process.\n\n"
        "Recommended Manual Tests:\n"
        "- Verify tamper resistance: Modify payload of a valid `wms_` token and verify Gateway returns 401.\n"
        "- Verify token expiration: Replay an expired `wms_` token after 12 hours.\n"
        "- Verify user key revocation: Revoke key in Convex and verify Redis cache invalidation."
    )

    result.evidence.append(
        create_evidence(
            evidence_type=EvidenceType.MANUAL,
            title="Authentication Verification Checklist",
            description="Verified auth architecture from Phase 3 source code inspection",
            response_data=auth_architecture_summary,
            source_file="api/_session.js",
        )
    )

    result.description = "Authentication architecture analyzed. Manual verification required for cryptographic tampering tests in staging."
    result.recommendation = "Maintain short TTLs on session tokens and ensure timing-safe secret comparisons across all key validation paths."
    result.completed_at = datetime.now(timezone.utc)
    return result
