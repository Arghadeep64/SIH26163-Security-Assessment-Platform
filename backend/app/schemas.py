"""Pydantic schemas and DTOs for SIH26163 platform."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Basic service status response schema."""

    project: str
    status: str


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str


class DatabaseHealthResponse(BaseModel):
    """Database health check response schema."""

    status: str
    database: str


class ScanCreateRequest(BaseModel):
    """Payload to initiate a new authorized security assessment."""

    target_url: str = Field(default="http://localhost:3000", description="Target URL of the authorized application")
    target_type: str = Field(default="LOCAL", description="Target type: LOCAL, AUTHORIZED_REMOTE, DEMO")


class ScanCreateResponse(BaseModel):
    """Response returned upon successfully queueing an assessment."""

    assessment_id: int
    status: str


class AssessmentResponse(BaseModel):
    """Detailed summary of an assessment session."""

    id: int
    target_url: str
    target_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    total_checks: Optional[int] = 0
    passed_checks: Optional[int] = 0
    failed_checks: Optional[int] = 0
    manual_checks: Optional[int] = 0
    error_checks: Optional[int] = 0
    critical_findings: Optional[int] = 0
    high_findings: Optional[int] = 0
    medium_findings: Optional[int] = 0
    low_findings: Optional[int] = 0
    info_findings: Optional[int] = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SecurityCheckResponse(BaseModel):
    """Result of an individual security check execution."""

    id: int
    assessment_id: int
    check_id: str
    category: str
    title: str
    status: str
    severity: Optional[str] = None
    description: Optional[str] = None
    affected_component: Optional[str] = None
    confidence: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FindingResponse(BaseModel):
    """Security finding entity."""

    id: int
    assessment_id: int
    check_id: Optional[int] = None
    finding_code: str
    title: str
    category: str
    severity: str
    status: str
    confidence: Optional[float] = None
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    description: Optional[str] = None
    affected_component: Optional[str] = None
    impact: Optional[str] = None
    reproduction_steps: Optional[str] = None
    remediation: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EvidenceResponse(BaseModel):
    """Technical evidence supporting a check or finding."""

    id: int
    assessment_id: int
    check_id: Optional[int] = None
    finding_id: Optional[int] = None
    evidence_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    request_data: Optional[str] = None
    response_data: Optional[str] = None
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    redacted: bool = True
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReportGenerateRequest(BaseModel):
    """Payload to trigger report generation for an assessment."""

    report_type: str = Field(default="HTML", description="Report format: HTML or PDF")


class ReportResponse(BaseModel):
    """Metadata response for a generated assessment report."""

    id: int
    assessment_id: int
    report_type: str
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    generated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

