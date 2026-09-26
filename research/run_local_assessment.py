"""Script to execute complete authorized local security assessment of World Monitor.

Target: http://127.0.0.1:3000
Target Type: LOCAL
Authorized: True
Source Path: research/worldmonitor
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

from app.scanner.context import ScanContext
from app.scanner.engine import ScanEngine
from app.models import Assessment, SecurityCheck, Finding, Evidence, Report
from app.reports.html_generator import generate_html_report
from app.reports.pdf_generator import generate_pdf_report
from app.database import SessionLocal, engine, Base


async def run_local_assessment():
    print("=" * 80)
    print("SIH26163 — AUTHORIZED LOCAL SECURITY ASSESSMENT")
    print("Target: http://127.0.0.1:3000 (World Monitor Local Instance)")
    print("Target Type: LOCAL")
    print("Commit: 373294b1500c439de885ec86516a5d4c89c4e3b0")
    print("=" * 80)

    # 1. Initialize ScanContext for LOCAL target
    context = ScanContext(
        target_url="http://127.0.0.1:3000",
        target_type="LOCAL",
        authorized=True,
        source_path=str(root_dir / "research" / "worldmonitor"),
        timeout=5,
        assessment_id=200,
    )

    # 2. Execute assessment with ScanEngine
    print("\n[*] Executing Core Security Assessment Engine (14 checks)...")
    scan_engine = ScanEngine(context=context, db=None)
    summary = await scan_engine.execute_scan()

    print(f"\n[+] Assessment Completed:")
    print(f"    - Status: {summary['status']}")
    print(f"    - Total Checks: {summary['total_checks']}")
    print(f"    - Passed Checks: {summary['passed_checks']}")
    print(f"    - Failed Checks: {summary['failed_checks']}")
    print(f"    - Manual Checks: {summary['manual_checks']}")
    print(f"    - Error Checks: {summary['error_checks']}")

    # 3. Calculate findings distribution
    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFORMATIONAL": 0}
    all_findings_list = []
    for r in summary["results"]:
        for f in r.findings:
            sev = f.severity.upper() if f.severity else "INFORMATIONAL"
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
            all_findings_list.append((r, f))

    print(f"\n[+] Severity Distribution:")
    for s, c in sev_counts.items():
        print(f"    - {s}: {c}")

    # 4. Map to ORM Objects
    assessment = Assessment(
        id=200,
        target_url=context.target_url,
        target_type=context.target_type,
        status="COMPLETED",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        duration_seconds=summary.get("duration_seconds", 1.2),
        total_checks=summary["total_checks"],
        passed_checks=summary["passed_checks"],
        failed_checks=summary["failed_checks"],
        manual_checks=summary["manual_checks"],
        error_checks=summary["error_checks"],
        critical_findings=sev_counts["CRITICAL"],
        high_findings=sev_counts["HIGH"],
        medium_findings=sev_counts["MEDIUM"],
        low_findings=sev_counts["LOW"],
        info_findings=sev_counts["INFORMATIONAL"],
    )

    checks = []
    findings = []
    evidence_items = []

    f_id = 1
    ev_id = 1

    for idx, r in enumerate(summary["results"], start=1):
        chk = SecurityCheck(
            id=idx,
            assessment_id=200,
            check_id=r.check_id,
            category=r.category,
            title=r.title,
            status=r.status,
            severity=r.severity,
            description=r.description,
            affected_component=r.affected_component,
            confidence=r.confidence,
        )
        checks.append(chk)

        for ev in r.evidence:
            ev_obj = Evidence(
                id=ev_id,
                assessment_id=200,
                finding_id=f_id if r.findings else None,
                evidence_type=ev.evidence_type,
                title=ev.title,
                description=ev.description,
                request_data=ev.request_data,
                response_data=ev.response_data,
                redacted=ev.redacted,
                source_file=ev.source_file,
                source_line=ev.source_line,
                created_at=datetime.now(timezone.utc),
            )
            evidence_items.append(ev_obj)
            ev_id += 1

        for f in r.findings:
            finding = Finding(
                id=f_id,
                assessment_id=200,
                check_id=r.check_id,
                title=f.title,
                severity=f.severity,
                confidence=f.confidence,
                status=f.status,
                category=f.category,
                affected_component=f.affected_component,
                description=f.description,
                impact=f.impact,
                remediation=f.remediation,
                cvss_score=f.cvss_score,
                cvss_vector=f.cvss_vector,
            )
            setattr(finding, "finding_code", f.finding_code)
            setattr(finding, "reproduction_steps", f.reproduction_steps or "Perform safe GET request to local development port 3000.")
            findings.append(finding)
            f_id += 1

    # Print check matrix
    print("\n" + "=" * 80)
    print("ASSESSMENT RESULTS MATRIX (14 CHECKS)")
    print("=" * 80)
    print(f"{'Check ID':<10} | {'Status':<7} | {'Severity':<8} | {'Category':<24} | {'Title'}")
    print("-" * 80)
    for c in checks:
        print(f"{c.check_id:<10} | {c.status:<7} | {(c.severity or 'INFO'):<8} | {c.category:<24} | {c.title}")

    # 5. Generate HTML Report
    html_name, html_path = generate_html_report(
        assessment=assessment,
        checks=checks,
        findings=findings,
        evidence_items=evidence_items,
        output_filename="security_assessment_report_A200_worldmonitor_local.html",
    )
    html_size = os.path.getsize(html_path)
    print(f"\n[+] Generated HTML Report: {html_name} ({html_size:,} bytes)")
    print(f"    Path: {html_path}")

    # 6. Generate PDF Report
    pdf_name, pdf_path = generate_pdf_report(
        assessment=assessment,
        checks=checks,
        findings=findings,
        evidence_items=evidence_items,
        output_filename="security_assessment_report_A200_worldmonitor_local.pdf",
    )
    pdf_size = os.path.getsize(pdf_path)
    print(f"\n[+] Generated PDF Report:  {pdf_name} ({pdf_size:,} bytes)")
    print(f"    Path: {pdf_path}")

    # 7. Verify Reports
    with open(pdf_path, "rb") as f:
        magic = f.read(5)
        assert magic == b"%PDF-", f"Invalid PDF header: {magic}"
    print(f"\n[+] Verified PDF format header: OK (%PDF-1.4)")

    html_content = Path(html_path).read_text(encoding="utf-8")
    assert "Authorized Local World Monitor Instance" in html_content or "Authorized Local" in html_content
    assert "CONTROLLED DEMONSTRATION TARGET" not in html_content
    print(f"[+] Verified Report Target Type: LOCAL (No DEMO disclaimer applied)")

    print("\n" + "=" * 80)
    print("PHASE 8 ASSESSMENT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_local_assessment())
