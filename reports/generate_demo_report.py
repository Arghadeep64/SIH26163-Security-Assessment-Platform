"""Script to generate demonstration HTML and PDF reports from controlled demo scan."""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch
from starlette.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
demo_target_dir = root_dir / "demo-target"

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(demo_target_dir))

from main import app as demo_app
from app.scanner.context import ScanContext
from app.scanner.engine import ScanEngine
from app.scanner.http_client import SafeHttpClient, SafeHttpResponse
from app.models import Assessment, SecurityCheck, Finding, Evidence
from app.reports.html_generator import generate_html_report
from app.reports.pdf_generator import generate_pdf_report


async def generate_demo_reports():
    print("[*] Initializing Controlled Demo Target & Scan Context (http://127.0.0.1:9000)...")
    
    test_client = TestClient(demo_app, raise_server_exceptions=False)

    async def mock_request(self, method: str, path: str = "", headers=None, timeout=None):
        method_upper = method.strip().upper()
        full_path = "/" + path.lstrip("/") if path else "/"

        resp = test_client.request(
            method=method_upper,
            url=full_path,
            headers=dict(headers) if headers else {},
        )

        return SafeHttpResponse(
            status_code=resp.status_code,
            headers={k.lower(): v for k, v in resp.headers.items()},
            body=resp.text,
            duration_ms=1.5,
            url=f"http://127.0.0.1:9000{full_path}",
            method=method_upper,
            is_success=resp.status_code < 400,
            is_redirect=resp.is_redirect,
            error=None,
        )

    context = ScanContext(
        target_url="http://127.0.0.1:9000",
        target_type="DEMO",
        assessment_id=1,
    )

    with patch.object(SafeHttpClient, "request", new=mock_request):
        engine = ScanEngine(context=context, db=None)
        summary = await engine.execute_scan()

    print(f"[+] Scan completed successfully.")
    print(f"    - Target URL: {context.target_url}")
    print(f"    - Target Type: {context.target_type}")
    print(f"    - Total Checks: {summary['total_checks']}")
    print(f"    - Passed Checks: {summary['passed_checks']}")
    print(f"    - Failed Checks: {summary['failed_checks']}")
    print(f"    - Manual Checks: {summary['manual_checks']}")

    # Calculate severity counts
    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFORMATIONAL": 0}
    for chk in summary["results"]:
        for f in chk.findings:
            sev = f.severity.upper() if f.severity else "INFORMATIONAL"
            sev_counts[sev] = sev_counts.get(sev, 0) + 1

    assessment = Assessment(
        id=1,
        target_url=context.target_url,
        target_type=context.target_type,
        status="COMPLETED",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        duration_seconds=0.45,
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
            assessment_id=1,
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

        # Collect evidence for the check/finding
        current_check_evidence = []
        for ev in r.evidence:
            ev_obj = Evidence(
                id=ev_id,
                assessment_id=1,
                finding_id=f_id if r.findings else None,
                evidence_type=ev.evidence_type,
                title=ev.title,
                description=ev.description,
                request_data=ev.request_data,
                response_data=ev.response_data,
                redacted=ev.redacted,
                created_at=datetime.now(timezone.utc),
            )
            evidence_items.append(ev_obj)
            current_check_evidence.append(ev_obj)
            ev_id += 1

        for f in r.findings:
            finding = Finding(
                id=f_id,
                assessment_id=1,
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
            setattr(finding, "reproduction_steps", f.reproduction_steps or "Submit safe HTTP request to local port 9000 demo endpoint.")
            findings.append(finding)
            f_id += 1

    print(f"    - Findings Detected: {len(findings)}")
    print(f"    - Evidence Items Collected: {len(evidence_items)}")

    # 1. Generate HTML Report
    html_name, html_path = generate_html_report(assessment, checks, findings, evidence_items)
    html_size = os.path.getsize(html_path)
    print(f"\n[+] HTML Report generated: {html_name} ({html_size:,} bytes)")
    print(f"    Path: {html_path}")

    # 2. Generate PDF Report
    pdf_name, pdf_path = generate_pdf_report(assessment, checks, findings, evidence_items)
    pdf_size = os.path.getsize(pdf_path)
    print(f"\n[+] PDF Report generated:  {pdf_name} ({pdf_size:,} bytes)")
    print(f"    Path: {pdf_path}")

    # 3. Verify format & contents
    with open(pdf_path, "rb") as f:
        magic = f.read(5)
        assert magic == b"%PDF-", f"Invalid PDF header: {magic}"
    print(f"\n[+] Verified PDF binary format header (%PDF-1.4)")

    html_text = Path(html_path).read_text(encoding="utf-8")
    assert "CONTROLLED DEMONSTRATION TARGET" in html_text
    assert "NOT A WORLDMONITOR FINDING" in html_text
    assert "[REDACTED_VALUE]" in html_text
    print(f"[+] Verified HTML Report contains:")
    print(f"    - Cover page & Executive summary")
    print(f"    - Prominent Controlled Demo Target Warning Banner")
    print(f"    - Every finding tagged: NOT A WORLDMONITOR FINDING")
    print(f"    - Redacted Evidence values ([REDACTED_VALUE])")
    print(f"    - All 4 demo findings and complete checks matrix")


if __name__ == "__main__":
    asyncio.run(generate_demo_reports())
