"""Tests for SafeHttpClient security guards and bounded execution."""

import pytest
from app.scanner.context import ScanContext
from app.scanner.http_client import SafeHttpClient


def test_safe_http_client_unauthorized_guard():
    """Verify scanner refuses to create client if authorized=False."""
    context = ScanContext(assessment_id=1, target_url="http://localhost:3000", authorized=False)
    with pytest.raises(PermissionError, match="must be explicitly authorized"):
        SafeHttpClient(context)


def test_safe_http_client_production_host_guard():
    """Verify scanner refuses to scan production worldmonitor.app automatically."""
    context = ScanContext(assessment_id=1, target_url="https://www.worldmonitor.app", authorized=True)
    with pytest.raises(PermissionError, match="Automated scanning against production target"):
        SafeHttpClient(context)


@pytest.mark.anyio
async def test_safe_http_client_disallowed_method():
    """Verify client rejects unsafe HTTP methods (e.g. POST/DELETE/PUT)."""
    context = ScanContext(assessment_id=1, target_url="http://localhost:3000", authorized=True)
    client = SafeHttpClient(context)
    with pytest.raises(ValueError, match="not in allowed safe assessment methods"):
        await client.request("POST", "/api/test")
    with pytest.raises(ValueError, match="not in allowed safe assessment methods"):
        await client.request("DELETE", "/api/test")


@pytest.mark.anyio
async def test_safe_http_client_connection_failure_handling():
    """Verify client handles unreachable hosts without unhandled crashes."""
    context = ScanContext(assessment_id=1, target_url="http://127.0.0.1:59999", authorized=True, timeout=1)
    client = SafeHttpClient(context)
    resp = await client.request("GET", "/test")
    assert resp.status_code == 0
    assert resp.is_success is False
    assert resp.error is not None
    assert "Network connection failed" in resp.error or "ConnectError" in resp.error
