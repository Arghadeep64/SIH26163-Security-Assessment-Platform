"""Tests for API status, health, and SPA frontend serving endpoints."""

from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app, INDEX_HTML

client = TestClient(app)


def test_api_status_endpoint():
    """Verify GET /api and /api/status return project ID and running status JSON."""
    response = client.get("/api")
    assert response.status_code == 200
    assert response.json() == {
        "project": "SIH26163",
        "status": "running",
    }

    response_status = client.get("/api/status")
    assert response_status.status_code == 200
    assert response_status.json() == {
        "project": "SIH26163",
        "status": "running",
    }


def test_root_endpoint_serves_frontend_or_fallback():
    """Verify GET / returns 200 (HTML SPA or JSON fallback)."""
    response = client.get("/")
    assert response.status_code == 200
    if INDEX_HTML.exists():
        assert "text/html" in response.headers.get("content-type", "")
    else:
        assert response.json().get("project") == "SIH26163"


def test_spa_frontend_route_fallback():
    """Verify frontend client routes (/dashboard, /findings) serve index.html with 200 OK."""
    response = client.get("/findings")
    assert response.status_code == 200
    if INDEX_HTML.exists():
        assert "text/html" in response.headers.get("content-type", "")


def test_api_404_returns_json_not_html():
    """Verify non-existent /api routes return a JSON 404 response rather than SPA index.html."""
    response = client.get("/api/non-existent-endpoint-probe")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_health_endpoint():
    """Verify GET /health returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_database_health_connected():
    """Verify GET /health/database returns connected when DB is reachable."""
    with patch("app.main.check_db_connection", return_value=True):
        response = client.get("/health/database")
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "database": "connected",
        }


def test_database_health_disconnected():
    """Verify GET /health/database returns disconnected when DB is unreachable."""
    with patch("app.main.check_db_connection", return_value=False):
        response = client.get("/health/database")
        assert response.status_code == 200
        assert response.json() == {
            "status": "unhealthy",
            "database": "disconnected",
        }


def test_database_health_live_fallback():
    """Verify GET /health/database runs gracefully without crashing if no live DB exists."""
    response = client.get("/health/database")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["status"] in ["healthy", "unhealthy"]
    assert data["database"] in ["connected", "disconnected"]
