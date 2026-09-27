"""API endpoints for managing and retrieving security assessments."""

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import Assessment, SecurityCheck, Finding, Evidence
from app.schemas import (
    ScanCreateRequest,
    ScanCreateResponse,
    AssessmentResponse,
    SecurityCheckResponse,
    FindingResponse,
    EvidenceResponse,
)
from app.scanner import ScanContext, ScanEngine

router = APIRouter(prefix="/scans", tags=["Assessments"])


async def run_scan_in_background(assessment_id: int, target_url: str, target_type: str) -> None:
    """Execute security scan workflow in background task with dedicated DB session."""
    db: Session = SessionLocal()
    try:
        context = ScanContext(
            assessment_id=assessment_id,
            target_url=target_url,
            target_type=target_type,
            authorized=True,
            source_path="research/worldmonitor",
        )
        engine = ScanEngine(context=context, db=db)
        await engine.execute_scan()
    finally:
        db.close()


@router.post("", response_model=ScanCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    payload: ScanCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ScanCreateResponse:
    """Initiate a new authorized security assessment against a target."""
    assessment = Assessment(
        target_url=payload.target_url,
        target_type=payload.target_type,
        status="QUEUED",
        created_at=datetime.now(timezone.utc),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # Dispatch background scan worker
    background_tasks.add_task(
        run_scan_in_background,
        assessment.id,
        payload.target_url,
        payload.target_type,
    )

    return ScanCreateResponse(
        assessment_id=assessment.id,
        status=assessment.status,
    )


@router.get("", response_model=list[AssessmentResponse])
async def list_scans(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[Assessment]:
    """Retrieve historical security assessment sessions."""
    return db.query(Assessment).order_by(Assessment.created_at.desc()).limit(limit).all()


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_scan(
    assessment_id: int,
    db: Session = Depends(get_db),
) -> Assessment:
    """Retrieve detailed status and counts for a specific assessment."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment session with ID {assessment_id} not found",
        )
    return assessment


@router.get("/{assessment_id}/checks", response_model=list[SecurityCheckResponse])
async def get_scan_checks(
    assessment_id: int,
    db: Session = Depends(get_db),
) -> list[SecurityCheck]:
    """Retrieve all security check results for an assessment session."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment session with ID {assessment_id} not found",
        )
    return db.query(SecurityCheck).filter(SecurityCheck.assessment_id == assessment_id).all()


@router.get("/{assessment_id}/findings", response_model=list[FindingResponse])
async def get_scan_findings(
    assessment_id: int,
    db: Session = Depends(get_db),
) -> list[Finding]:
    """Retrieve all findings identified during an assessment session."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment session with ID {assessment_id} not found",
        )
    return db.query(Finding).filter(Finding.assessment_id == assessment_id).all()


@router.get("/{assessment_id}/evidence", response_model=list[EvidenceResponse])
async def get_scan_evidence(
    assessment_id: int,
    check_id: Optional[int] = None,
    finding_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> list[Evidence]:
    """Retrieve technical evidence entries collected during an assessment session."""
    query = db.query(Evidence).filter(Evidence.assessment_id == assessment_id)
    if check_id is not None:
        query = query.filter(Evidence.check_id == check_id)
    if finding_id is not None:
        query = query.filter(Evidence.finding_id == finding_id)
    return query.all()
