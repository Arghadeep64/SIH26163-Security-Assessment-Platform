"""Tests for core ScanEngine execution and error resilience."""

from unittest.mock import patch, AsyncMock
import pytest

from app.scanner.context import ScanContext
from app.scanner.engine import ScanEngine
from app.scanner.models import CheckResult, CheckStatus, SeverityLevel


@pytest.mark.anyio
async def test_scan_engine_unauthorized_fails():
    """Verify ScanEngine raises PermissionError if context is not authorized."""
    context = ScanContext(assessment_id=1, target_url="http://localhost:3000", authorized=False)
    engine = ScanEngine(context=context, db=None)
    with pytest.raises(PermissionError, match="must be explicitly authorized"):
        await engine.execute_scan()


@pytest.mark.anyio
async def test_scan_engine_full_execution_without_db():
    """Verify ScanEngine runs all checks and aggregates counters properly."""
    context = ScanContext(
        assessment_id=1,
        target_url="http://localhost:3000",
        target_type="LOCAL",
        authorized=True,
        source_path="research/worldmonitor",
        timeout=1,
    )
    engine = ScanEngine(context=context, db=None)
    summary = await engine.execute_scan()

    assert summary["status"] == "COMPLETED"
    assert summary["total_checks"] >= 14
    assert summary["total_checks"] == (
        summary["passed_checks"]
        + summary["failed_checks"]
        + summary["manual_checks"]
        + summary["error_checks"]
    )
    assert len(summary["results"]) >= 14


@pytest.mark.anyio
async def test_scan_engine_resilience_on_check_error():
    """Verify ScanEngine continues running even if an individual check throws an exception."""
    context = ScanContext(
        assessment_id=1,
        target_url="http://localhost:3000",
        authorized=True,
        source_path="research/worldmonitor",
        timeout=1,
    )

    async def throwing_check(ctx):
        raise RuntimeError("Simulated unexpected crash in check")

    with patch("app.scanner.engine.get_registered_checks", return_value=[throwing_check]):
        engine = ScanEngine(context=context, db=None)
        summary = await engine.execute_scan()

        assert summary["status"] == "COMPLETED"
        assert summary["total_checks"] == 1
        assert summary["error_checks"] == 1
        assert summary["results"][0].status == CheckStatus.ERROR.value
        assert "Simulated unexpected crash" in summary["results"][0].description
