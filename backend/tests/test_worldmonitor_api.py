"""Tests for World Monitor dedicated API endpoints."""

import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_worldmonitor_overview_endpoint():
    """Verify /api/worldmonitor/overview returns valid structured metadata."""
    response = client.get("/api/worldmonitor/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "SIH26163"
    assert "primary_target" in data
    assert data["primary_target"]["name"] == "World Monitor"
    assert data["primary_target"]["production_url"] == "https://www.worldmonitor.app"
    assert "assessment_verdict" in data
    assert len(data["security_domains_assessed"]) >= 7


def test_worldmonitor_source_audit_endpoint():
    """Verify /api/worldmonitor/source-audit returns structured security domains."""
    response = client.get("/api/worldmonitor/source-audit")
    assert response.status_code == 200
    data = response.json()
    assert data["repository"] == "koala73/worldmonitor"
    assert len(data["audit_categories"]) >= 4
    for cat in data["audit_categories"]:
        assert "category" in cat
        assert "component" in cat
        assert len(cat["source_files"]) > 0
        assert len(cat["verified_controls"]) > 0
        assert "assessment_verdict" in cat
