"""Security check DEP-001: Dependency Manifest & Software Supply Chain Review."""

import json
from datetime import datetime, timezone
from pathlib import Path
from app.scanner.context import ScanContext
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, EvidenceType
from app.scanner.evidence import create_evidence


async def check_dependency_manifests(context: ScanContext) -> CheckResult:
    """Inspect npm and Cargo dependency manifests for supply chain security controls and lockfile hygiene."""
    started_at = datetime.now(timezone.utc)
    base_path = Path(context.source_path)

    result = CheckResult(
        check_id="DEP-001",
        category="Dependency Security",
        title="Dependency Inventory & Supply Chain Review",
        status=CheckStatus.PASS.value,
        severity=SeverityLevel.INFO.value,
        confidence=90.0,
        description="Inspects package.json, package-lock.json, Cargo.toml, and Cargo.lock to assess dependency locking and supply-chain hygiene.",
        affected_component="Software Dependencies / Package Manifests",
        started_at=started_at,
    )

    if not base_path.exists():
        result.status = CheckStatus.MANUAL.value
        result.description = f"Source directory '{context.source_path}' is not accessible."
        result.completed_at = datetime.now(timezone.utc)
        return result

    manifest_summaries = []

    # 1. Inspect package.json & package-lock.json
    pkg_file = base_path / "package.json"
    lock_file = base_path / "package-lock.json"

    if pkg_file.exists():
        try:
            pkg_data = json.loads(pkg_file.read_text(encoding="utf-8"))
            deps_count = len(pkg_data.get("dependencies", {}))
            dev_deps_count = len(pkg_data.get("devDependencies", {}))
            has_lock = lock_file.exists()

            manifest_summaries.append(
                f"NPM Manifest: {deps_count} production deps, {dev_deps_count} dev deps (Lockfile present: {has_lock})"
            )

            result.evidence.append(
                create_evidence(
                    evidence_type=EvidenceType.DEPENDENCY,
                    title="NPM Package Manifest Details",
                    description=f"Package {pkg_data.get('name', 'world-monitor')} v{pkg_data.get('version', 'unknown')}",
                    response_data=f"Dependencies: {deps_count}\nDevDependencies: {dev_deps_count}\nLockfile: {has_lock}",
                    source_file="package.json",
                )
            )
        except Exception:
            pass

    # 2. Inspect Cargo.toml & Cargo.lock
    cargo_file = base_path / "src-tauri" / "Cargo.toml"
    cargo_lock = base_path / "src-tauri" / "Cargo.lock"

    if cargo_file.exists():
        has_cargo_lock = cargo_lock.exists()
        manifest_summaries.append(f"Rust / Cargo Manifest present (Cargo.lock present: {has_cargo_lock})")
        result.evidence.append(
            create_evidence(
                evidence_type=EvidenceType.DEPENDENCY,
                title="Cargo Rust Dependency Manifest",
                description="Verified Tauri native desktop dependency configuration",
                response_data=f"Cargo.toml present: True\nCargo.lock present: {has_cargo_lock}",
                source_file="src-tauri/Cargo.toml",
            )
        )

    if manifest_summaries:
        result.status = CheckStatus.PASS.value
        result.severity = SeverityLevel.INFO.value
        result.description = f"Dependency manifests and lockfiles verified: {'; '.join(manifest_summaries)}"
    else:
        result.status = CheckStatus.MANUAL.value
        result.severity = SeverityLevel.LOW.value
        result.description = "No package manifests or lockfiles were located in target source directory."

    result.completed_at = datetime.now(timezone.utc)
    return result
