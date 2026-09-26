"""Tests for Assessment and Findings API endpoints."""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import Assessment, SecurityCheck, Finding

client = TestClient(app)


def test_create_scan_endpoint():
    """Verify POST /api/scans queues a scan and returns 201 Created."""
    mock_db = MagicMock()
    mock_assessment = Assessment(id=1, target_url="http://localhost:3000", target_type="LOCAL", status="QUEUED")
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock(side_effect=lambda a: setattr(a, "id", 1))

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        with patch("app.api.scans.run_scan_in_background") as mock_bg:
            response = client.post(
                "/api/scans",
                json={"target_url": "http://localhost:3000", "target_type": "LOCAL"},
            )
            assert response.status_code == 201
            data = response.json()
            assert data["assessment_id"] == 1
            assert data["status"] == "QUEUED"
    finally:
        app.dependency_overrides.clear()


def test_get_scan_endpoint_not_found():
    """Verify GET /api/scans/{id} returns 404 if assessment does not exist."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/api/scans/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_get_scan_endpoint_found():
    """Verify GET /api/scans/{id} returns assessment details."""
    mock_db = MagicMock()
    mock_assessment = Assessment(
        id=1,
        target_url="http://localhost:3000",
        target_type="LOCAL",
        status="COMPLETED",
        total_checks=14,
        passed_checks=10,
        failed_checks=2,
        manual_checks=2,
        error_checks=0,
        critical_findings=0,
        high_findings=0,
        medium_findings=0,
        low_findings=0,
        info_findings=0,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_assessment

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/api/scans/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["status"] == "COMPLETED"
        assert data["total_checks"] == 14
    finally:
        app.dependency_overrides.clear()


def test_list_findings_endpoint():
    """Verify GET /api/findings returns findings with optional filters."""
    mock_db = MagicMock()
    mock_finding = Finding(
        id=1,
        assessment_id=1,
        finding_code="FINDING-SRC-001",
        title="Security-Sensitive Code Sinks Identified in Source",
        category="Source Code Security",
        severity="LOW",
        status="MANUAL_VERIFICATION",
    )
    mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_finding]

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/api/findings")
        assert response.status_code == 200
        findings = response.json()
        assert len(findings) == 1
        assert findings[0]["finding_code"] == "FINDING-SRC-001"
    finally:
        app.dependency_overrides.clear()
