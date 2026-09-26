"""Assessment execution engine orchestrating check execution, evidence collection, and persistence."""

import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.scanner.context import ScanContext
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel, FindingStatus
from app.scanner.registry import get_registered_checks
from app.models import Assessment, SecurityCheck, Finding, Evidence

logger = logging.getLogger("sih26163.scanner")


class ScanEngine:
    """Core security assessment engine coordinating check execution and database persistence."""

    def __init__(self, context: ScanContext, db: Optional[Session] = None):
        self.context = context
        self.db = db

    async def execute_scan(self) -> dict:
        """Run all registered security checks and persist results."""
        if not self.context.authorized:
            raise PermissionError("ScanContext must be explicitly authorized to execute assessment.")

        started_at = datetime.now(timezone.utc)
        logger.info("Starting security assessment %d on target %s", self.context.assessment_id, self.context.target_url)

        assessment = None
        if self.db:
            assessment = self.db.query(Assessment).filter(Assessment.id == self.context.assessment_id).first()
            if assessment:
                assessment.status = "RUNNING"
                assessment.started_at = started_at
                self.db.commit()

        checks = get_registered_checks()
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        manual_checks = 0
        error_checks = 0

        critical_findings = 0
        high_findings = 0
        medium_findings = 0
        low_findings = 0
        info_findings = 0

        results: list[CheckResult] = []

        for check_fn in checks:
            check_start = datetime.now(timezone.utc)
            try:
                check_result = await check_fn(self.context)
            except Exception as exc:
                logger.exception("Check %s failed with internal error", getattr(check_fn, "__name__", "unknown"))
                check_result = CheckResult(
                    check_id="ERR-CHK",
                    category="Engine",
                    title="Security Check Execution Failure",
                    status=CheckStatus.ERROR.value,
                    severity=SeverityLevel.HIGH.value,
                    confidence=100.0,
                    description=f"Internal engine error executing check: {str(exc)}",
                    affected_component="Scan Engine",
                    started_at=check_start,
                    completed_at=datetime.now(timezone.utc),
                )

            total_checks += 1
            if check_result.status == CheckStatus.PASS.value:
                passed_checks += 1
            elif check_result.status == CheckStatus.FAIL.value:
                failed_checks += 1
            elif check_result.status == CheckStatus.MANUAL.value:
                manual_checks += 1
            elif check_result.status == CheckStatus.ERROR.value:
                error_checks += 1

            # Count findings by severity
            for finding in check_result.findings:
                sev = (finding.severity or "").upper()
                if sev == SeverityLevel.CRITICAL.value:
                    critical_findings += 1
                elif sev == SeverityLevel.HIGH.value:
                    high_findings += 1
                elif sev == SeverityLevel.MEDIUM.value:
                    medium_findings += 1
                elif sev == SeverityLevel.LOW.value:
                    low_findings += 1
                elif sev == SeverityLevel.INFO.value:
                    info_findings += 1

            results.append(check_result)

            # Persist to database if active DB session is available
            if self.db and assessment:
                try:
                    db_check = SecurityCheck(
                        assessment_id=assessment.id,
                        check_id=check_result.check_id,
                        category=check_result.category,
                        title=check_result.title,
                        status=check_result.status,
                        severity=check_result.severity,
                        description=check_result.description,
                        affected_component=check_result.affected_component,
                        confidence=check_result.confidence,
                        started_at=check_result.started_at or check_start,
                        completed_at=check_result.completed_at or datetime.now(timezone.utc),
                    )
                    self.db.add(db_check)
                    self.db.flush()  # Populates db_check.id

                    # Persist evidence
                    for ev in check_result.evidence:
                        db_evidence = Evidence(
                            assessment_id=assessment.id,
                            check_id=db_check.id,
                            evidence_type=ev.evidence_type,
                            title=ev.title,
                            description=ev.description,
                            request_data=ev.request_data,
                            response_data=ev.response_data,
                            source_file=ev.source_file,
                            source_line=ev.source_line,
                            redacted=ev.redacted,
                        )
                        self.db.add(db_evidence)

                    # Persist findings
                    for f in check_result.findings:
                        # Ensure finding code is unique by suffixing assessment ID if needed
                        unique_finding_code = f"{f.finding_code}-A{assessment.id}"
                        db_finding = Finding(
                            assessment_id=assessment.id,
                            check_id=db_check.id,
                            finding_code=unique_finding_code,
                            title=f.title,
                            category=f.category,
                            severity=f.severity,
                            status=f.status or FindingStatus.MANUAL_VERIFICATION.value,
                            confidence=f.confidence,
                            cvss_score=f.cvss_score,
                            cvss_vector=f.cvss_vector,
                            description=f.description,
                            affected_component=f.affected_component,
                            impact=f.impact,
                            reproduction_steps=f.reproduction_steps,
                            remediation=f.remediation,
                        )
                        self.db.add(db_finding)

                    self.db.commit()
                except Exception:
                    self.db.rollback()
                    logger.exception("Failed to persist security check record to database")

        completed_at = datetime.now(timezone.utc)
        duration_seconds = (completed_at - started_at).total_seconds()

        if self.db and assessment:
            try:
                assessment.status = "COMPLETED"
                assessment.completed_at = completed_at
                assessment.duration_seconds = duration_seconds
                assessment.total_checks = total_checks
                assessment.passed_checks = passed_checks
                assessment.failed_checks = failed_checks
                assessment.manual_checks = manual_checks
                assessment.error_checks = error_checks
                assessment.critical_findings = critical_findings
                assessment.high_findings = high_findings
                assessment.medium_findings = medium_findings
                assessment.low_findings = low_findings
                assessment.info_findings = info_findings
                self.db.commit()
            except Exception:
                self.db.rollback()
                logger.exception("Failed to finalize assessment in database")

        logger.info(
            "Assessment %d finished in %.2fs: %d total, %d pass, %d fail, %d manual, %d error",
            self.context.assessment_id,
            duration_seconds,
            total_checks,
            passed_checks,
            failed_checks,
            manual_checks,
            error_checks,
        )

        return {
            "assessment_id": self.context.assessment_id,
            "status": "COMPLETED",
            "duration_seconds": duration_seconds,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "manual_checks": manual_checks,
            "error_checks": error_checks,
            "critical_findings": critical_findings,
            "high_findings": high_findings,
            "medium_findings": medium_findings,
            "low_findings": low_findings,
            "info_findings": info_findings,
            "results": results,
        }
