"""SQLAlchemy ORM models for SIH26163 Security Assessment Platform.

Database schema is managed via external SQL scripts:
- database/mysql/sih26163_schema.sql
- database/tidb/sih26163_schema.sql

Note: Base.metadata.create_all() is intentionally not called at startup.
"""

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Assessment(Base):
    """Stores security assessment and scanning sessions."""

    __tablename__ = "assessments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    target_url = Column(String(500), nullable=False)
    target_type = Column(String(50), default="LOCAL")
    status = Column(String(30), nullable=False, default="QUEUED", index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Numeric(10, 2), nullable=True)
    total_checks = Column(Integer, nullable=False, default=0)
    passed_checks = Column(Integer, nullable=False, default=0)
    failed_checks = Column(Integer, nullable=False, default=0)
    manual_checks = Column(Integer, nullable=False, default=0)
    error_checks = Column(Integer, nullable=False, default=0)
    critical_findings = Column(Integer, nullable=False, default=0)
    high_findings = Column(Integer, nullable=False, default=0)
    medium_findings = Column(Integer, nullable=False, default=0)
    low_findings = Column(Integer, nullable=False, default=0)
    info_findings = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    security_checks = relationship(
        "SecurityCheck",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    findings = relationship(
        "Finding",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    evidence_items = relationship(
        "Evidence",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    reports = relationship(
        "Report",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )


class SecurityCheck(Base):
    """Stores individual security check results per assessment."""

    __tablename__ = "security_checks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    assessment_id = Column(
        BigInteger,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    check_id = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False, index=True)
    severity = Column(String(30), nullable=True)
    description = Column(Text, nullable=True)
    affected_component = Column(String(500), nullable=True)
    confidence = Column(Numeric(5, 2), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="security_checks")
    findings = relationship("Finding", back_populates="security_check")
    evidence_items = relationship("Evidence", back_populates="security_check")


class Finding(Base):
    """Stores confirmed or potential security findings."""

    __tablename__ = "findings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    assessment_id = Column(
        BigInteger,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    check_id = Column(
        BigInteger,
        ForeignKey("security_checks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    finding_code = Column(String(50), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    severity = Column(String(30), nullable=False, index=True)
    status = Column(String(30), nullable=False, index=True)
    confidence = Column(Numeric(5, 2), nullable=True)
    cvss_score = Column(Numeric(3, 1), nullable=True)
    cvss_vector = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    affected_component = Column(String(500), nullable=True)
    impact = Column(Text, nullable=True)
    reproduction_steps = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    assessment = relationship("Assessment", back_populates="findings")
    security_check = relationship("SecurityCheck", back_populates="findings")
    evidence_items = relationship("Evidence", back_populates="finding")


class Evidence(Base):
    """Stores technical evidence supporting a check or finding."""

    __tablename__ = "evidence"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    assessment_id = Column(
        BigInteger,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    check_id = Column(
        BigInteger,
        ForeignKey("security_checks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    finding_id = Column(
        BigInteger,
        ForeignKey("findings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    evidence_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    request_data = Column(Text, nullable=True)
    response_data = Column(Text, nullable=True)
    source_file = Column(String(500), nullable=True)
    source_line = Column(Integer, nullable=True)
    redacted = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="evidence_items")
    security_check = relationship("SecurityCheck", back_populates="evidence_items")
    finding = relationship("Finding", back_populates="evidence_items")


class Report(Base):
    """Stores metadata for generated assessment report files."""

    __tablename__ = "reports"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    assessment_id = Column(
        BigInteger,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    report_type = Column(String(30), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    generated_at = Column(DateTime, nullable=False, default=func.now())
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="reports")
