"""Reports API endpoints for generating, querying, and downloading security assessment reports."""

import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report, Assessment
from app.schemas import ReportGenerateRequest, ReportResponse
from app.reports.generator import generate_assessment_report
from app.reports.html_generator import get_safe_reports_directory

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/{assessment_id}/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    assessment_id: int,
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
) -> Report:
    """Generate a new professional security assessment report (HTML or PDF) for an assessment."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment session with ID {assessment_id} not found",
        )

    try:
        report_data = generate_assessment_report(
            assessment_id=assessment_id,
            report_type=payload.report_type,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(exc)}",
        )

    report = db.query(Report).filter(Report.id == report_data["id"]).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Report was generated but record could not be retrieved.",
        )
    return report


@router.get("", response_model=list[ReportResponse])
async def list_all_reports(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[Report]:
    """Retrieve all historical generated security reports across assessments."""
    return db.query(Report).order_by(Report.created_at.desc()).limit(limit).all()


@router.get("/{assessment_id}", response_model=list[ReportResponse])
async def list_assessment_reports(
    assessment_id: int,
    db: Session = Depends(get_db),
) -> list[Report]:
    """Retrieve all generated report files for a specific assessment session."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment session with ID {assessment_id} not found",
        )
    return db.query(Report).filter(Report.assessment_id == assessment_id).order_by(Report.created_at.desc()).all()


@router.get("/download/{report_id}")
async def download_report_file(
    report_id: int,
    db: Session = Depends(get_db),
):
    """Safely download a generated report file by its record ID."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not report.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found",
        )

    file_path = Path(report.file_path).resolve()
    reports_dir = get_safe_reports_directory()

    # Strict path traversal security check
    if not str(file_path).startswith(str(reports_dir)) or not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested report file is unavailable or outside permitted storage boundaries.",
        )

    media_type = "application/pdf" if report.report_type == "PDF" else "text/html"
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=report.file_name,
    )


@router.get("/view/{report_id}")
async def view_report_file(
    report_id: int,
    db: Session = Depends(get_db),
):
    """Safely render an HTML report directly in the browser or stream PDF for preview."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not report.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found",
        )

    file_path = Path(report.file_path).resolve()
    reports_dir = get_safe_reports_directory()

    # Strict path traversal security check
    if not str(file_path).startswith(str(reports_dir)) or not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested report file is unavailable or outside permitted storage boundaries.",
        )

    if report.report_type == "HTML":
        html_content = file_path.read_text(encoding="utf-8", errors="replace")
        return HTMLResponse(content=html_content, status_code=200)

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=report.file_name,
    )
