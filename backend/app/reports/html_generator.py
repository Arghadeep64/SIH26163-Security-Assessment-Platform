"""HTML Security Assessment Report Generator using Jinja2 templates."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models import Assessment, SecurityCheck, Finding, Evidence

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
GENERATED_REPORTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "reports" / "generated"


def get_safe_reports_directory() -> Path:
    """Ensure and return the canonical directory for storing generated reports."""
    GENERATED_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return GENERATED_REPORTS_DIR.resolve()


def generate_html_report(
    assessment: Assessment,
    checks: list[SecurityCheck],
    findings: list[Finding],
    evidence_items: list[Evidence],
    output_filename: Optional[str] = None,
) -> tuple[str, str]:
    """Generate a self-contained HTML assessment report.
    
    Returns:
        tuple[str, str]: (filename, absolute_file_path)
    """
    reports_dir = get_safe_reports_directory()
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    if not output_filename:
        output_filename = f"security_assessment_report_A{assessment.id}_{timestamp_str}.html"
    
    # Path traversal protection: Ensure filename contains only safe characters
    safe_filename = Path(output_filename).name
    destination_path = (reports_dir / safe_filename).resolve()
    
    # Verify the destination is strictly inside reports_dir
    if not str(destination_path).startswith(str(reports_dir)):
        raise ValueError("Path traversal attempt detected in report generation output path.")

    # Attach evidence items to corresponding findings for rendering
    evidence_by_finding: dict[int, list[Evidence]] = {}
    evidence_by_check: dict[int, list[Evidence]] = {}
    for ev in evidence_items:
        if ev.finding_id:
            evidence_by_finding.setdefault(ev.finding_id, []).append(ev)
        if ev.check_id:
            evidence_by_check.setdefault(ev.check_id, []).append(ev)

    for f in findings:
        f_evidence = evidence_by_finding.get(f.id, [])
        if not f_evidence and f.check_id:
            f_evidence = evidence_by_check.get(f.check_id, [])
        setattr(f, "evidence_items", f_evidence)

    # Initialize Jinja2 environment with autoescaping
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("report.html")

    is_demo = (
        assessment.target_type == "DEMO"
        or "9000" in str(assessment.target_url)
        or "demo-target" in str(assessment.target_url)
    )

    confirmed_findings = [
        f for f in findings
        if (f.status in ("CONFIRMED", "OPEN") or is_demo)
        and f.status not in ("ENVIRONMENT_OBSERVATION", "SOURCE_REVIEW", "INFORMATIONAL")
    ]
    observations = [
        f for f in findings
        if f.status in ("ENVIRONMENT_OBSERVATION", "SOURCE_REVIEW", "INFORMATIONAL")
        or f not in confirmed_findings
    ]
    # Deduplicate while preserving order
    observations = [f for f in observations if f not in confirmed_findings]

    rendered_html = template.render(
        assessment=assessment,
        checks=checks,
        findings=findings,
        confirmed_findings=confirmed_findings,
        observations=observations,
        is_demo=is_demo,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )

    destination_path.write_text(rendered_html, encoding="utf-8")
    return safe_filename, str(destination_path)
