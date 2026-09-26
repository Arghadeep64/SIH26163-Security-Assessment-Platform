"""Findings API endpoints for querying and filtering security findings."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Finding
from app.schemas import FindingResponse

router = APIRouter(prefix="/findings", tags=["Findings"])


@router.get("", response_model=list[FindingResponse])
async def list_findings(
    severity: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[Finding]:
    """Retrieve security findings across assessments with optional severity and status filters."""
    query = db.query(Finding)
    if severity:
        query = query.filter(Finding.severity == severity.upper())
    if status_filter:
        query = query.filter(Finding.status == status_filter.upper())
    return query.order_by(Finding.created_at.desc()).limit(limit).all()


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding(
    finding_id: int,
    db: Session = Depends(get_db),
) -> Finding:
    """Retrieve detailed information for a specific security finding."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding with ID {finding_id} not found",
        )
    return finding
