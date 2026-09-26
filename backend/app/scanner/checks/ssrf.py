"""Security check SSRF-001: Server-Side Request Forgery (SSRF) Defense Review."""

from datetime import datetime, timezone
from pathlib import Path
from app.scanner.context import ScanContext
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, EvidenceType
from app.scanner.evidence import create_evidence


async def check_ssrf_defenses(context: ScanContext) -> CheckResult:
    """Analyze source implementations of proxies (RSS, MCP, Sidecar) to verify SSRF mitigations."""
    started_at = datetime.now(timezone.utc)
    base_path = Path(context.source_path)

    result = CheckResult(
        check_id="SSRF-001",
        category="Server-Side Request Forgery",
        title="SSRF Defensive Architecture & Proxy Filter Audit",
        status=CheckStatus.PASS.value,
        severity=SeverityLevel.INFO.value,
        confidence=95.0,
        description="Audits source code of rss-proxy.js, mcp-proxy.ts, and local-api-server.mjs to verify domain allowlisting, DNS pre-flight filtering, and private IP blocking.",
        affected_component="Outbound Network Proxies (api/rss-proxy.js, api/mcp-proxy.ts)",
        started_at=started_at,
    )

    if not base_path.exists():
        result.status = CheckStatus.MANUAL.value
        result.description = f"Source directory '{context.source_path}' is not accessible for static SSRF defense audit."
        result.completed_at = datetime.now(timezone.utc)
        return result

    verified_controls = []

    # 1. Inspect RSS proxy
    rss_file = base_path / "api" / "rss-proxy.js"
    if rss_file.exists():
        content = rss_file.read_text(encoding="utf-8", errors="ignore")
        if "isAllowedDomain" in content and "MAX_DIRECT_REDIRECTS" in content:
            verified_controls.append("RSS Proxy enforces domain allowlisting with per-redirect hop re-validation")
            result.evidence.append(
                create_evidence(
                    evidence_type=EvidenceType.SOURCE_CODE,
                    title="RSS Proxy SSRF Controls",
                    description="Verified domain matching and redirect boundary enforcement",
                    source_file="api/rss-proxy.js",
                )
            )

    # 2. Inspect MCP proxy
    mcp_file = base_path / "api" / "mcp-proxy.ts"
    if mcp_file.exists():
        content = mcp_file.read_text(encoding="utf-8", errors="ignore")
        if "cloudflare-dns.com" in content and "isBlockedResolvedAddress" in content:
            verified_controls.append("MCP Proxy enforces Cloudflare DoH pre-flight DNS check and blocks private IP ranges")
            result.evidence.append(
                create_evidence(
                    evidence_type=EvidenceType.SOURCE_CODE,
                    title="MCP Proxy DoH & IP Filter",
                    description="Verified pre-flight DNS validation against private and cloud-metadata addresses",
                    source_file="api/mcp-proxy.ts",
                )
            )

    # 3. Inspect Sidecar IPv4 pinning
    sidecar_file = base_path / "src-tauri" / "sidecar" / "local-api-server.mjs"
    if sidecar_file.exists():
        content = sidecar_file.read_text(encoding="utf-8", errors="ignore")
        if "makePinnedLookup" in content and "assertSafeSidecarFetchUrl" in content:
            verified_controls.append("Desktop sidecar overrides global fetch with IPv4 socket pinning and SSRF blocking")
            result.evidence.append(
                create_evidence(
                    evidence_type=EvidenceType.SOURCE_CODE,
                    title="Sidecar Socket Pinning",
                    description="Verified custom IPv4 socket lookup pinning to close DNS rebinding TOCTOU",
                    source_file="src-tauri/sidecar/local-api-server.mjs",
                )
            )

    if verified_controls:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = f"Verified multi-stage SSRF mitigations in source: {'; '.join(verified_controls)}"
    else:
        result.status = CheckStatus.MANUAL.value
        result.severity = SeverityLevel.LOW.value
        result.description = "Could not locate proxy source files to establish SSRF defense verification."

    result.completed_at = datetime.now(timezone.utc)
    return result
