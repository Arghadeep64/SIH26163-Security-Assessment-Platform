"""Tests for API status and health endpoints."""

from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify GET / returns project ID and running status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "project": "SIH26163",
        "status": "running",
    }


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
