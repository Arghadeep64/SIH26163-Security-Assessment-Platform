"""Tests for Security Assessment Report Generation (HTML and PDF)."""

import os
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models import Assessment, SecurityCheck, Finding, Evidence, Report
from app.reports.html_generator import generate_html_report
from app.reports.pdf_generator import generate_pdf_report

client = TestClient(app)


def _create_mock_demo_assessment():
    """Helper to create a populated mock demo assessment with findings and evidence."""
    assessment = Assessment(
        id=42,
        target_url="http://127.0.0.1:9000",
        target_type="DEMO",
        status="COMPLETED",
        started_at=datetime(2026, 9, 26, 10, 0, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 9, 26, 10, 5, 0, tzinfo=timezone.utc),
        total_checks=14,
        passed_checks=8,
        failed_checks=4,
        manual_checks=2,
        error_checks=0,
        critical_findings=0,
        high_findings=1,
        medium_findings=2,
        low_findings=1,
        info_findings=0,
    )

    finding1 = Finding(
        id=101,
        assessment_id=42,
        check_id="WEB-001",
        title="Missing Security Headers in HTTP Response",
        severity="MEDIUM",
        confidence=95,
        status="OPEN",
        category="Web Security",
        affected_component="HTTP Response Headers",
        description="The application response is missing critical HTTP security headers: Content-Security-Policy, Strict-Transport-Security, X-Frame-Options.",
        impact="Increases risk of Cross-Site Scripting (XSS), clickjacking, and MIME sniffing attacks.",
        remediation="Configure server to return Content-Security-Policy, X-Frame-Options, and Strict-Transport-Security headers.",
        cvss_score=None,
        cvss_vector=None,
    )

    finding2 = Finding(
        id=102,
        assessment_id=42,
        check_id="WEB-002",
        title="Permissive Cross-Origin Resource Sharing (CORS) Policy",
        severity="HIGH",
        confidence=90,
        status="OPEN",
        category="Web Security",
        affected_component="CORS Middleware",
        description="The CORS header Access-Control-Allow-Origin is configured to wildcard '*' or reflects arbitrary origins.",
        impact="Allows unauthorized domains to read sensitive authenticated responses.",
        remediation="Restrict Access-Control-Allow-Origin to trusted origins.",
        cvss_score=None,
        cvss_vector=None,
    )

    finding3 = Finding(
        id=103,
        assessment_id=42,
        check_id="AUTH-001",
        title="Insecure Session Cookie Flags",
        severity="MEDIUM",
        confidence=100,
        status="OPEN",
        category="Authentication",
        affected_component="Session Cookie Management",
        description="Session cookies are transmitted without HttpOnly and SameSite=Strict flags.",
        impact="Session tokens can be accessed via malicious JavaScript.",
        remediation="Set HttpOnly, Secure, and SameSite=Strict on all session cookies.",
        cvss_score=None,
        cvss_vector=None,
    )

    finding4 = Finding(
        id=104,
        assessment_id=42,
        check_id="INFO-001",
        title="Excessive Server Version and Debug Disclosure",
        severity="LOW",
        confidence=85,
        status="OPEN",
        category="Information Disclosure",
        affected_component="Server Response Banner",
        description="Server headers disclose detailed software stack versions and internal debug paths.",
        impact="Aids attackers in fingerprinting technologies and targeting known CVEs.",
        remediation="Remove Server and X-Powered-By banners in production configuration.",
        cvss_score=None,
        cvss_vector=None,
    )

    evidence1 = Evidence(
        id=201,
        finding_id=101,
        assessment_id=42,
        evidence_type="HTTP_HEADER",
        title="Missing Headers",
        description="Raw HTTP response headers",
        response_data="Missing headers: Content-Security-Policy, X-Frame-Options",
        redacted=False,
        created_at=datetime(2026, 9, 26, 10, 1, 0, tzinfo=timezone.utc),
    )

    evidence2 = Evidence(
        id=202,
        finding_id=103,
        assessment_id=42,
        evidence_type="COOKIE",
        title="Session Cookie",
        description="Observed cookie value",
        response_data="Set-Cookie: demo_session=[REDACTED_VALUE]; Path=/",
        redacted=True,
        created_at=datetime(2026, 9, 26, 10, 2, 0, tzinfo=timezone.utc),
    )

    check1 = SecurityCheck(
        id=1,
        assessment_id=42,
        check_id="WEB-001",
        title="Security Headers",
        category="Web Security",
        status="FAIL",
        severity="MEDIUM",
        confidence=95,
        description="Missing critical security headers",
    )

    check2 = SecurityCheck(
        id=2,
        assessment_id=42,
        check_id="WEB-002",
        title="CORS Configuration",
        category="Web Security",
        status="FAIL",
        severity="HIGH",
        confidence=90,
        description="Wildcard origin allowed",
    )

    check3 = SecurityCheck(
        id=3,
        assessment_id=42,
        check_id="AUTH-001",
        title="Cookie Security Flags",
        category="Authentication",
        status="FAIL",
        severity="MEDIUM",
        confidence=100,
        description="Insecure cookie flags detected",
    )

    check4 = SecurityCheck(
        id=4,
        assessment_id=42,
        check_id="INFO-001",
        title="Banner & Version Disclosure",
        category="Information Disclosure",
        status="FAIL",
        severity="LOW",
        confidence=85,
        description="Server headers exposed",
    )

    check5 = SecurityCheck(
        id=5,
        assessment_id=42,
        check_id="AUTH-MANUAL-001",
        title="Authentication Workflow Analysis",
        category="Authentication",
        status="MANUAL",
        severity="INFORMATIONAL",
        confidence=50,
        description="Requires manual analyst review",
    )

    checks = [check1, check2, check3, check4, check5]
    findings = [finding1, finding2, finding3, finding4]
    evidences = [evidence1, evidence2]

    return assessment, checks, findings, evidences


def test_html_report_generation_file_and_content():
    """Verify HTML report generation writes a valid HTML file with required sections."""
    assessment, checks, findings, evidences = _create_mock_demo_assessment()

    file_name, file_path = generate_html_report(
        assessment=assessment,
        checks=checks,
        findings=findings,
        evidence_items=evidences,
    )

    assert os.path.exists(file_path)
    content = Path(file_path).read_text(encoding="utf-8")

    # Verify structural sections
    assert "<!DOCTYPE html>" in content
    assert "SIH26163" in content
    assert "SECURITY ASSESSMENT REPORT" in content
    assert "CONTROLLED DEMONSTRATION TARGET" in content
    assert "NOT A WORLDMONITOR FINDING" in content
    assert "Executive Summary" in content
    assert "Assessment Methodology" in content
    assert "Vulnerability Findings" in content
    assert "Manual Verification Items" in content
    assert "Assessment Limitations" in content
    assert "Conclusion" in content

    # Verify findings are present
    assert "Missing Security Headers in HTTP Response" in content
    assert "Permissive Cross-Origin Resource Sharing (CORS) Policy" in content
    assert "Insecure Session Cookie Flags" in content
    assert "Excessive Server Version and Debug Disclosure" in content

    # Verify redacted evidence is preserved
    assert "[REDACTED_VALUE]" in content


def test_pdf_report_generation_file_and_header():
    """Verify PDF report generation creates a valid, non-empty PDF file with %PDF magic header."""
    assessment, checks, findings, evidences = _create_mock_demo_assessment()

    file_name, file_path = generate_pdf_report(
        assessment=assessment,
        checks=checks,
        findings=findings,
        evidence_items=evidences,
    )

    assert os.path.exists(file_path)
    assert os.path.getsize(file_path) > 1000

    # Read binary header
    with open(file_path, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-"


def test_html_escaping_in_report():
    """Verify XSS payloads in target_url or findings are escaped in HTML report."""
    assessment = Assessment(
        id=99,
        target_url="http://example.com/<script>alert(1)</script>",
        target_type="LOCAL",
        status="COMPLETED",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        total_checks=1,
        passed_checks=0,
        failed_checks=1,
        manual_checks=0,
        error_checks=0,
        critical_findings=0,
        high_findings=1,
        medium_findings=0,
        low_findings=0,
        info_findings=0,
    )
    finding = Finding(
        id=999,
        assessment_id=99,
        check_id="TEST-001",
        title="XSS Test <img src=x onerror=alert('xss')>",
        severity="HIGH",
        confidence=90,
        status="OPEN",
        category="Test",
        affected_component="<script>document.cookie</script>",
        description="Description with <b>bold</b> and <script>attack()</script>",
        impact="Impact <script>",
        remediation="Fix it <script>",
        cvss_score=None,
        cvss_vector=None,
    )

    file_name, file_path = generate_html_report(
        assessment=assessment,
        checks=[],
        findings=[finding],
        evidence_items=[],
    )

    content = Path(file_path).read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in content
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in content
    assert "<script>attack()</script>" not in content


def test_empty_assessment_report():
    """Verify an assessment with 0 findings generates a clean report stating 0 findings."""
    assessment = Assessment(
        id=50,
        target_url="http://127.0.0.1:3000",
        target_type="LOCAL",
        status="COMPLETED",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        total_checks=5,
        passed_checks=5,
        failed_checks=0,
        manual_checks=0,
        error_checks=0,
        critical_findings=0,
        high_findings=0,
        medium_findings=0,
        low_findings=0,
        info_findings=0,
    )

    file_name, file_path = generate_html_report(
        assessment=assessment,
        checks=[],
        findings=[],
        evidence_items=[],
    )

    content = Path(file_path).read_text(encoding="utf-8")
    assert "No vulnerability findings were identified" in content


def test_api_generate_html_report():
    """Verify POST /api/reports/{id}/generate creates an HTML report and stores in DB."""
    mock_db = MagicMock()
    assessment, checks, findings, evidences = _create_mock_demo_assessment()

    mock_report = Report(
        id=1,
        assessment_id=42,
        report_type="HTML",
        file_name="security_report_42.html",
        file_path="reports/generated/security_report_42.html",
        generated_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    def query_mock(model):
        q = MagicMock()
        if model == Assessment:
            q.filter.return_value.first.return_value = assessment
        elif model == SecurityCheck:
            q.filter.return_value.all.return_value = checks
        elif model == Finding:
            q.filter.return_value.all.return_value = findings
        elif model == Evidence:
            q.filter.return_value.all.return_value = evidences
        elif model == Report:
            q.filter.return_value.first.return_value = mock_report
            q.filter.return_value.order_by.return_value.all.return_value = [mock_report]
            q.order_by.return_value.limit.return_value.all.return_value = [mock_report]
        return q

    mock_db.query.side_effect = query_mock
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock(side_effect=lambda r: setattr(r, "id", 1))

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.post(
            "/api/reports/42/generate",
            json={"report_type": "HTML"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["assessment_id"] == 42
        assert data["report_type"] == "HTML"
        assert data["file_name"].endswith(".html")
    finally:
        app.dependency_overrides.clear()


def test_api_generate_pdf_report():
    """Verify POST /api/reports/{id}/generate creates a PDF report."""
    mock_db = MagicMock()
    assessment, checks, findings, evidences = _create_mock_demo_assessment()

    mock_report = Report(
        id=2,
        assessment_id=42,
        report_type="PDF",
        file_name="security_report_42.pdf",
        file_path="reports/generated/security_report_42.pdf",
        generated_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    def query_mock(model):
        q = MagicMock()
        if model == Assessment:
            q.filter.return_value.first.return_value = assessment
        elif model == SecurityCheck:
            q.filter.return_value.all.return_value = checks
        elif model == Finding:
            q.filter.return_value.all.return_value = findings
        elif model == Evidence:
            q.filter.return_value.all.return_value = evidences
        elif model == Report:
            q.filter.return_value.first.return_value = mock_report
            q.filter.return_value.order_by.return_value.all.return_value = [mock_report]
            q.order_by.return_value.limit.return_value.all.return_value = [mock_report]
        return q

    mock_db.query.side_effect = query_mock
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock(side_effect=lambda r: setattr(r, "id", 2))

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.post(
            "/api/reports/42/generate",
            json={"report_type": "PDF"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["assessment_id"] == 42
        assert data["report_type"] == "PDF"
        assert data["file_name"].endswith(".pdf")
    finally:
        app.dependency_overrides.clear()


def test_api_generate_report_not_found():
    """Verify POST /api/reports/{id}/generate returns 404 for nonexistent assessment."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.post(
            "/api/reports/999/generate",
            json={"report_type": "HTML"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


def test_api_get_assessment_reports():
    """Verify GET /api/reports/{assessment_id} returns list of reports."""
    mock_db = MagicMock()
    assessment, _, _, _ = _create_mock_demo_assessment()
    mock_report = Report(
        id=1,
        assessment_id=42,
        report_type="HTML",
        file_name="report_42_HTML.html",
        file_path="reports/generated/report_42_HTML.html",
        generated_at=datetime(2026, 9, 26, 10, 30, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 9, 26, 10, 30, 0, tzinfo=timezone.utc),
    )

    def query_mock(model):
        q = MagicMock()
        if model == Assessment:
            q.filter.return_value.first.return_value = assessment
        elif model == Report:
            q.filter.return_value.order_by.return_value.all.return_value = [mock_report]
        return q

    mock_db.query.side_effect = query_mock

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/api/reports/42")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["report_type"] == "HTML"
    finally:
        app.dependency_overrides.clear()


def test_api_download_path_traversal_protection():
    """Verify download endpoint rejects attempts with path traversal characters."""
    mock_db = MagicMock()
    mock_report = Report(
        id=99,
        assessment_id=42,
        report_type="HTML",
        file_name="../../etc/passwd",
        file_path="../../etc/passwd",
        generated_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_report

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/api/reports/download/99")
        assert response.status_code in [400, 404]
    finally:
        app.dependency_overrides.clear()
