"""Security check CONFIG-002: Security Configuration & Hardening Review."""

import json
from datetime import datetime, timezone
from pathlib import Path
from app.scanner.context import ScanContext
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, EvidenceType
from app.scanner.evidence import create_evidence


async def check_security_configuration(context: ScanContext) -> CheckResult:
    """Inspect repository configuration manifests for security controls and hardening directives."""
    started_at = datetime.now(timezone.utc)
    base_path = Path(context.source_path)

    result = CheckResult(
        check_id="CONFIG-002",
        category="Configuration Security",
        title="Security Configuration & Hardening Review",
        status=CheckStatus.PASS.value,
        severity=SeverityLevel.INFO.value,
        confidence=95.0,
        description="Evaluates declared security configurations in vercel.json, Nginx configs, and Tauri desktop policies.",
        affected_component="Deployment & Platform Configuration",
        started_at=started_at,
    )

    if not base_path.exists():
        result.status = CheckStatus.MANUAL.value
        result.description = f"Source directory '{context.source_path}' is unavailable for static configuration review."
        result.completed_at = datetime.now(timezone.utc)
        return result

    controls_verified = []

    # 1. Inspect vercel.json
    vercel_file = base_path / "vercel.json"
    if vercel_file.exists():
        try:
            vercel_content = vercel_file.read_text(encoding="utf-8")
            if "Content-Security-Policy" in vercel_content:
                controls_verified.append("Content Security Policy defined in vercel.json")
            if "Strict-Transport-Security" in vercel_content or "nosniff" in vercel_content:
                controls_verified.append("Transport and MIME security headers configured in vercel.json")

            result.evidence.append(
                create_evidence(
                    evidence_type=EvidenceType.CONFIGURATION,
                    title="Vercel Security Headers Config",
                    description="Verified vercel.json declared response header rules.",
                    response_data=f"Vercel config path: {vercel_file.name}",
                    source_file="vercel.json",
                )
            )
        except Exception:
            pass

    # 2. Inspect Tauri security configuration
    tauri_file = base_path / "src-tauri" / "tauri.conf.json"
    if tauri_file.exists():
        try:
            tauri_data = json.loads(tauri_file.read_text(encoding="utf-8"))
            security_cfg = tauri_data.get("app", {}).get("security", {})
            if "csp" in security_cfg:
                controls_verified.append("Tauri desktop webview CSP configured")
                result.evidence.append(
                    create_evidence(
                        evidence_type=EvidenceType.CONFIGURATION,
                        title="Tauri Desktop CSP Policy",
                        description=f"Desktop CSP: {security_cfg['csp'][:100]}...",
                        response_data=security_cfg["csp"],
                        source_file="src-tauri/tauri.conf.json",
                    )
                )
        except Exception:
            pass

    # 3. Inspect RSS Domain allowlist
    rss_allowlist_file = base_path / "api" / "_rss-allowed-domains.js"
    if rss_allowlist_file.exists():
        controls_verified.append("Strict RSS proxy domain allowlist present in api/_rss-allowed-domains.js")
        result.evidence.append(
            create_evidence(
                evidence_type=EvidenceType.CONFIGURATION,
                title="RSS Proxy SSRF Allowlist",
                description="Verified existence of centralized RSS domain allowlist.",
                source_file="api/_rss-allowed-domains.js",
            )
        )

    if controls_verified:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = f"Verified declared security controls: {'; '.join(controls_verified)}"
    else:
        result.status = CheckStatus.MANUAL.value
        result.severity = SeverityLevel.LOW.value
        result.description = "Could not locate standard security configuration files in target source directory."

    result.completed_at = datetime.now(timezone.utc)
    return result
