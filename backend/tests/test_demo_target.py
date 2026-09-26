"""Tests for SIH26163 Controlled Demo Target and Scanner Detection Engine."""

import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock
import pytest
from starlette.testclient import TestClient

# Ensure demo-target is importable
demo_target_path = Path(__file__).resolve().parent.parent.parent / "demo-target"
if str(demo_target_path) not in sys.path:
    sys.path.insert(0, str(demo_target_path))

from main import app as demo_app  # demo-target/main.py
from app.scanner.context import ScanContext
from app.scanner.engine import ScanEngine
from app.scanner.http_client import SafeHttpClient, SafeHttpResponse
from app.scanner.models import CheckStatus, SeverityLevel, FindingStatus
from app.scanner.checks.headers import check_security_headers
from app.scanner.checks.cors import check_cors_policy
from app.scanner.checks.cookies import check_cookie_security
from app.scanner.checks.information_disclosure import check_information_disclosure


# ==============================================================================
# 1. DEMO TARGET APP UNIT TESTS
# ==============================================================================


def test_demo_target_root_banner():
    """Verify demo target root endpoint returns the mandatory identification banner."""
    client = TestClient(demo_app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "SIH26163 Controlled Security Demo Target"
    assert data["warning"] == "INTENTIONALLY VULNERABLE LOCAL TEST APPLICATION"
    assert data["environment"] == "LOCAL DEMO ONLY"

    # Verify intentional absence of security headers
    assert "Content-Security-Policy" not in response.headers
    assert "X-Content-Type-Options" not in response.headers
    assert "Referrer-Policy" not in response.headers

    # Verify presence of X-Powered-By disclosure header
    assert "FastAPI-Controlled-Demo-Server" in response.headers.get("X-Powered-By", "")

    # Verify presence of insecure demo session cookie
    assert "demo_session" in response.cookies
    assert response.cookies["demo_session"] == "controlled-demo-value"


def test_demo_target_data_endpoint_and_cors():
    """Verify /api/demo-data returns non-sensitive dummy data and permissive CORS."""
    client = TestClient(demo_app)

    # Test GET request with arbitrary origin
    test_origin = "https://unauthorized-third-party.example.com"
    response = client.get("/api/demo-data", headers={"Origin": test_origin})

    assert response.status_code == 200
    data = response.json()
    assert data["environment"] == "demo"
    assert data["message"] == "Controlled demonstration data"
    assert "password" not in str(data).lower()
    assert "token" not in str(data).lower()

    # Verify permissive CORS reflection
    assert response.headers.get("access-control-allow-origin") == test_origin
    assert response.headers.get("access-control-allow-credentials") == "true"

    # Test OPTIONS preflight
    preflight = client.options("/api/demo-data", headers={"Origin": test_origin})
    assert preflight.status_code == 200
    assert preflight.headers.get("access-control-allow-origin") == test_origin
    assert preflight.headers.get("access-control-allow-credentials") == "true"


def test_demo_target_error_endpoint_disclosure():
    """Verify /api/demo-error returns simulated internal path information."""
    client = TestClient(demo_app, raise_server_exceptions=False)
    response = client.get("/api/demo-error")

    assert response.status_code == 500
    data = response.json()
    assert r"C:\demo\application\example.py" in data["file"]
    assert "UnhandledDemoException" in data["error"]
    assert "Traceback" in data["stack_trace"]


def test_demo_target_health_endpoint():
    """Verify harmless health check endpoint."""
    client = TestClient(demo_app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["environment"] == "demo"


# ==============================================================================
# 2. SCANNER DETECTION TESTS AGAINST DEMO TARGET
# ==============================================================================


@pytest.fixture
def demo_scan_context():
    """ScanContext configured specifically for the local demo target on port 9000."""
    return ScanContext(
        assessment_id=900,
        target_url="http://127.0.0.1:9000",
        target_type="DEMO",
        authorized=True,
        source_path="demo-target",
        timeout=2,
    )


@pytest.fixture
def mock_demo_http_client(demo_scan_context):
    """Adapter routing SafeHttpClient requests directly to TestClient(demo_app)."""
    test_client = TestClient(demo_app, raise_server_exceptions=False)

    async def mock_request(self, method: str, path: str = "", headers=None, timeout=None):
        method_upper = method.strip().upper()
        full_path = "/" + path.lstrip("/") if path else "/"

        resp = test_client.request(
            method=method_upper,
            url=full_path,
            headers=dict(headers) if headers else {},
        )

        return SafeHttpResponse(
            status_code=resp.status_code,
            headers={k.lower(): v for k, v in resp.headers.items()},
            body=resp.text,
            duration_ms=1.5,
            url=f"http://127.0.0.1:9000{full_path}",
            method=method_upper,
            is_success=resp.status_code < 400,
            is_redirect=resp.is_redirect,
            error=None,
        )

    return mock_request


@pytest.mark.anyio
async def test_scanner_detects_missing_headers_on_demo_target(demo_scan_context, mock_demo_http_client):
    """WEB-001: Scanner detects missing headers and labels finding as controlled demo finding."""
    with patch.object(SafeHttpClient, "request", new=mock_demo_http_client):
        result = await check_security_headers(demo_scan_context)

        assert result.status == CheckStatus.FAIL.value
        assert result.severity == SeverityLevel.MEDIUM.value
        assert len(result.findings) == 1

        finding = result.findings[0]
        assert finding.finding_code == "FINDING-WEB-001"
        assert "[CONTROLLED DEMO FINDING — NOT A WORLDMONITOR FINDING]" in finding.title
        assert finding.status == FindingStatus.CONFIRMED.value
        assert finding.remediation is not None
        assert len(result.evidence) >= 1


@pytest.mark.anyio
async def test_scanner_detects_permissive_cors_on_demo_target(demo_scan_context, mock_demo_http_client):
    """WEB-002: Scanner detects permissive CORS on demo target."""
    with patch.object(SafeHttpClient, "request", new=mock_demo_http_client):
        result = await check_cors_policy(demo_scan_context)

        assert result.status == CheckStatus.FAIL.value
        assert result.severity == SeverityLevel.HIGH.value
        assert len(result.findings) == 1

        finding = result.findings[0]
        assert finding.finding_code == "FINDING-WEB-002"
        assert "[CONTROLLED DEMO FINDING — NOT A WORLDMONITOR FINDING]" in finding.title
        assert "Arbitrary third-party origin reflected" in result.description
        assert finding.status == FindingStatus.CONFIRMED.value
        assert len(result.evidence) >= 1


@pytest.mark.anyio
async def test_scanner_detects_insecure_cookie_and_redacts(demo_scan_context, mock_demo_http_client):
    """WEB-003: Scanner detects insecure cookie flags and confirms secret value is redacted."""
    with patch.object(SafeHttpClient, "request", new=mock_demo_http_client):
        result = await check_cookie_security(demo_scan_context)

        assert result.status == CheckStatus.FAIL.value
        assert len(result.findings) == 1

        finding = result.findings[0]
        assert finding.finding_code == "FINDING-WEB-003"
        assert "[CONTROLLED DEMO FINDING — NOT A WORLDMONITOR FINDING]" in finding.title
        assert "demo_session" in finding.title

        # Verify redaction: The raw cookie value "controlled-demo-value" MUST be redacted in evidence
        evidence = result.evidence[0]
        assert "controlled-demo-value" not in evidence.response_data
        assert "[REDACTED_VALUE]" in evidence.response_data


@pytest.mark.anyio
async def test_scanner_detects_information_disclosure(demo_scan_context, mock_demo_http_client):
    """CONFIG-001: Scanner detects simulated internal path disclosure."""
    with patch.object(SafeHttpClient, "request", new=mock_demo_http_client):
        result = await check_information_disclosure(demo_scan_context)

        assert result.status == CheckStatus.FAIL.value
        assert result.severity == SeverityLevel.LOW.value
        assert len(result.findings) == 1

        finding = result.findings[0]
        assert finding.finding_code == "FINDING-CONFIG-001"
        assert "[CONTROLLED DEMO FINDING — NOT A WORLDMONITOR FINDING]" in finding.title
        assert "C:\\demo\\application\\example.py" in str(result.description) or "X-Powered-By" in str(result.description)


# ==============================================================================
# 3. END-TO-END SCAN ENGINE VALIDATION
# ==============================================================================


@pytest.mark.anyio
async def test_scan_engine_e2e_against_demo_target(demo_scan_context, mock_demo_http_client):
    """Verify complete end-to-end ScanEngine run against demo target."""
    with patch.object(SafeHttpClient, "request", new=mock_demo_http_client):
        engine = ScanEngine(context=demo_scan_context, db=None)
        summary = await engine.execute_scan()

        assert summary["status"] == "COMPLETED"
        assert summary["total_checks"] >= 14
        assert summary["failed_checks"] >= 4  # Headers, CORS, Cookies, Info Disclosure

        # Ensure all generated findings are labeled as controlled demo findings
        all_findings = []
        for chk in summary["results"]:
            all_findings.extend(chk.findings)

        demo_findings = [f for f in all_findings if "[CONTROLLED DEMO FINDING" in f.title]
        assert len(demo_findings) >= 4

        # Verify finding codes present
        finding_codes = {f.finding_code for f in demo_findings}
        assert "FINDING-WEB-001" in finding_codes
        assert "FINDING-WEB-002" in finding_codes
        assert "FINDING-WEB-003" in finding_codes
        assert "FINDING-CONFIG-001" in finding_codes


# ==============================================================================
# 4. SAFETY RESTRICTIONS VALIDATION
# ==============================================================================


def test_safety_restriction_blocks_production():
    """Verify scanner immediately blocks any attempt to target production World Monitor."""
    production_context = ScanContext(
        assessment_id=999,
        target_url="https://www.worldmonitor.app",
        authorized=True,
    )
    with pytest.raises(PermissionError, match="prohibited by SIH26163 policy"):
        SafeHttpClient(production_context)


@pytest.mark.anyio
async def test_safety_restriction_blocks_destructive_methods(demo_scan_context):
    """Verify scanner strictly prohibits state-changing methods (POST, PUT, DELETE, PATCH)."""
    client = SafeHttpClient(demo_scan_context)
    for forbidden_method in ["POST", "PUT", "DELETE", "PATCH"]:
        with pytest.raises(ValueError, match="not in allowed safe assessment methods"):
            await client.request(forbidden_method, "/api/demo-data")
