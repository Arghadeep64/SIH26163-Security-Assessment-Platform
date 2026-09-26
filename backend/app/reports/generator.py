"""Report generation orchestrator coordinating HTML/PDF generators and database persistence."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Assessment, SecurityCheck, Finding, Evidence, Report
from app.reports.html_generator import generate_html_report, get_safe_reports_directory
from app.reports.pdf_generator import generate_pdf_report

logger = logging.getLogger("sih26163.reports")


def generate_assessment_report(
    assessment_id: int,
    report_type: str = "HTML",
    db: Optional[Session] = None,
) -> dict:
    """Orchestrate report generation for a specified assessment and persist record.
    
    Args:
        assessment_id: Unique integer identifier of the assessment.
        report_type: Format requested ('HTML' or 'PDF').
        db: Active SQLAlchemy session.
        
    Returns:
        dict: Generated report metadata.
    """
    normalized_type = report_type.strip().upper()
    if normalized_type not in ("HTML", "PDF"):
        raise ValueError(f"Unsupported report format '{report_type}'. Only 'HTML' and 'PDF' are supported.")

    assessment = None
    checks = []
    findings = []
    evidence_items = []

    if db:
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment session with ID {assessment_id} not found.")

        checks = db.query(SecurityCheck).filter(SecurityCheck.assessment_id == assessment_id).all()
        findings = db.query(Finding).filter(Finding.assessment_id == assessment_id).all()
        evidence_items = db.query(Evidence).filter(Evidence.assessment_id == assessment_id).all()
    else:
        # Standalone generation fallback (e.g. unit testing with mock assessment)
        raise ValueError("Active database session required to query assessment data.")

    # Generate requested report format
    if normalized_type == "HTML":
        file_name, file_path = generate_html_report(
            assessment=assessment,
            checks=checks,
            findings=findings,
            evidence_items=evidence_items,
        )
    else:
        file_name, file_path = generate_pdf_report(
            assessment=assessment,
            checks=checks,
            findings=findings,
            evidence_items=evidence_items,
        )

    generated_at = datetime.now(timezone.utc)
    report_record = None

    if db:
        try:
            report_record = Report(
                assessment_id=assessment.id,
                report_type=normalized_type,
                file_name=file_name,
                file_path=file_path,
                generated_at=generated_at,
            )
            db.add(report_record)
            db.commit()
            db.refresh(report_record)
        except Exception:
            db.rollback()
            logger.exception("Failed to persist report metadata record to database.")

    return {
        "id": report_record.id if report_record else 1,
        "assessment_id": assessment.id,
        "report_type": normalized_type,
        "file_name": file_name,
        "file_path": file_path,
        "generated_at": generated_at,
    }
