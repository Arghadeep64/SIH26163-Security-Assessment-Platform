"""Tests for individual security check modules."""

from unittest.mock import patch, AsyncMock
import pytest

from app.scanner.context import ScanContext
from app.scanner.http_client import SafeHttpResponse
from app.scanner.models import CheckStatus
from app.scanner.checks import (
    check_security_headers,
    check_cors_policy,
    check_cookie_security,
    check_tls_configuration,
    check_information_disclosure,
    check_source_security_patterns,
    check_security_configuration,
    check_dependency_manifests,
    check_api_discovery,
    check_rate_limiting_policy,
    check_authentication_architecture,
    check_authorization_boundaries,
    check_ssrf_defenses,
    check_tauri_desktop_security,
)


@pytest.fixture
def local_context():
    return ScanContext(
        assessment_id=1,
        target_url="http://localhost:3000",
        target_type="LOCAL",
        authorized=True,
        source_path="research/worldmonitor",
    )


@pytest.fixture
def demo_context():
    return ScanContext(
        assessment_id=2,
        target_url="http://127.0.0.1:9000",
        target_type="DEMO",
        authorized=True,
        source_path="demo-target",
    )


@pytest.mark.anyio
async def test_check_security_headers_pass(local_context):
    """Verify check_security_headers passes when headers are present."""
    mock_resp = SafeHttpResponse(
        status_code=200,
        headers={
            "content-security-policy": "default-src 'self'",
            "x-content-type-options": "nosniff",
            "referrer-policy": "strict-origin-when-cross-origin",
            "permissions-policy": "camera=()",
        },
        body="<html>OK</html>",
        duration_ms=10.0,
        url="http://localhost:3000/",
        method="GET",
        is_success=True,
        is_redirect=False,
    )
    with patch("app.scanner.http_client.SafeHttpClient.request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_resp
        result = await check_security_headers(local_context)
        assert result.check_id == "WEB-001"
        assert result.status == CheckStatus.PASS.value
        assert len(result.evidence) > 0


@pytest.mark.anyio
async def test_check_security_headers_missing_local_classification(local_context):
    """Verify missing headers on local environment are classified as ENVIRONMENT_OBSERVATION."""
    mock_resp = SafeHttpResponse(
        status_code=200,
        headers={},
        body="<html>OK</html>",
        duration_ms=10.0,
        url="http://localhost:3000/",
        method="GET",
        is_success=True,
        is_redirect=False,
    )
    with patch("app.scanner.http_client.SafeHttpClient.request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_resp
        result = await check_security_headers(local_context)
        assert result.check_id == "WEB-001"
        assert result.status == CheckStatus.MANUAL.value
        assert len(result.findings) == 1
        finding = result.findings[0]
        assert finding.status == "ENVIRONMENT_OBSERVATION"
        assert "Development Environment Security Header Observation" in finding.title
        assert "An application vulnerability is not established" in finding.description


@pytest.mark.anyio
async def test_check_security_headers_missing_demo_classification(demo_context):
    """Verify missing headers on demo target are classified as CONFIRMED controlled demo finding."""
    mock_resp = SafeHttpResponse(
        status_code=200,
        headers={},
        body="<html>OK</html>",
        duration_ms=10.0,
        url="http://127.0.0.1:9000/",
        method="GET",
        is_success=True,
        is_redirect=False,
    )
    with patch("app.scanner.http_client.SafeHttpClient.request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_resp
        result = await check_security_headers(demo_context)
        assert result.check_id == "WEB-001"
        assert result.status == CheckStatus.FAIL.value
        assert len(result.findings) == 1
        finding = result.findings[0]
        assert finding.status == "CONFIRMED"
        assert "[CONTROLLED DEMO FINDING — NOT A WORLDMONITOR FINDING]" in finding.title


@pytest.mark.anyio
async def test_check_cors_policy(local_context):
    """Verify check_cors_policy flags wildcard with credentials."""
    mock_resp = SafeHttpResponse(
        status_code=204,
        headers={
            "access-control-allow-origin": "*",
            "access-control-allow-credentials": "true",
        },
        body="",
        duration_ms=10.0,
        url="http://localhost:3000/api/health",
        method="OPTIONS",
        is_success=True,
        is_redirect=False,
    )
    with patch("app.scanner.http_client.SafeHttpClient.request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_resp
        result = await check_cors_policy(local_context)
        assert result.check_id == "WEB-002"
        assert result.status == CheckStatus.FAIL.value


@pytest.mark.anyio
async def test_check_cookie_security(local_context):
    """Verify check_cookie_security evaluates Set-Cookie attributes."""
    mock_resp = SafeHttpResponse(
        status_code=200,
        headers={"set-cookie": "token=secret_val; HttpOnly; SameSite=Lax"},
        body="",
        duration_ms=10.0,
        url="http://localhost:3000/",
        method="GET",
        is_success=True,
        is_redirect=False,
    )
    with patch("app.scanner.http_client.SafeHttpClient.request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_resp
        result = await check_cookie_security(local_context)
        assert result.check_id == "WEB-003"
        assert result.status == CheckStatus.PASS.value


@pytest.mark.anyio
async def test_check_security_headers_unreachable_timeout(local_context):
    """Verify unreachable target on WEB-001 is classified as MANUAL with liveness evidence."""
    mock_resp = SafeHttpResponse(
        status_code=0,
        headers={},
        body="",
        duration_ms=5000.0,
        url="https://remote.example.com/",
        method="GET",
        is_success=False,
        is_redirect=False,
        error="Network connection failed: ConnectTimeout ()",
    )
    with patch("app.scanner.http_client.SafeHttpClient.request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_resp
        result = await check_security_headers(local_context)
        assert result.check_id == "WEB-001"
        assert result.status == CheckStatus.MANUAL.value
        assert "Target was unreachable" in result.description
        assert len(result.evidence) > 0


@pytest.mark.anyio
async def test_check_tls_configuration_localhost(local_context):
    """Verify check_tls_configuration handles localhost HTTP cleanly."""
    result = await check_tls_configuration(local_context)
    assert result.check_id == "WEB-004"
    assert result.status == CheckStatus.PASS.value


@pytest.mark.anyio
async def test_check_tls_configuration_unreachable_timeout():
    """Verify network connection timeout on HTTPS target is classified as MANUAL."""
    remote_ctx = ScanContext(
        assessment_id=3,
        target_url="https://remote.example.com",
        target_type="AUTHORIZED_REMOTE",
        authorized=True,
    )
    mock_resp = SafeHttpResponse(
        status_code=0,
        headers={},
        body="",
        duration_ms=5000.0,
        url="https://remote.example.com/",
        method="GET",
        is_success=False,
        is_redirect=False,
        error="Network connection failed: ConnectTimeout ()",
    )
    with patch("app.scanner.http_client.SafeHttpClient.request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_resp
        result = await check_tls_configuration(remote_ctx)
        assert result.check_id == "WEB-004"
        assert result.status == CheckStatus.MANUAL.value
        assert "Target was unreachable for TLS handshake" in result.description


@pytest.mark.anyio
async def test_check_tls_configuration_certificate_error():
    """Verify genuine SSL/TLS certificate verification failure is classified as ERROR."""
    remote_ctx = ScanContext(
        assessment_id=4,
        target_url="https://invalid-cert.example.com",
        target_type="AUTHORIZED_REMOTE",
        authorized=True,
    )
    mock_resp = SafeHttpResponse(
        status_code=0,
        headers={},
        body="",
        duration_ms=500.0,
        url="https://invalid-cert.example.com/",
        method="GET",
        is_success=False,
        is_redirect=False,
        error="Network connection failed: ConnectError ([SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed)",
    )
    with patch("app.scanner.http_client.SafeHttpClient.request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_resp
        result = await check_tls_configuration(remote_ctx)
        assert result.check_id == "WEB-004"
        assert result.status == CheckStatus.ERROR.value
        assert "TLS handshake or connection failed" in result.description


@pytest.mark.anyio
async def test_check_information_disclosure(local_context):
    """Verify check_information_disclosure flags stack traces in response body."""
    mock_resp = SafeHttpResponse(
        status_code=500,
        headers={"x-powered-by": "Express"},
        body="Traceback (most recent call last):\nFile '/app/main.py', line 42 in run",
        duration_ms=10.0,
        url="http://localhost:3000/health",
        method="GET",
        is_success=False,
        is_redirect=False,
    )
    with patch("app.scanner.http_client.SafeHttpClient.request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_resp
        result = await check_information_disclosure(local_context)
        assert result.check_id == "CONFIG-001"
        assert result.status == CheckStatus.FAIL.value


@pytest.mark.anyio
async def test_source_and_config_checks(local_context):
    """Verify static source, config, and dependency checks execute on research/worldmonitor."""
    res_src = await check_source_security_patterns(local_context)
    assert res_src.check_id == "SOURCE-001"
    assert res_src.status in [CheckStatus.PASS.value, CheckStatus.MANUAL.value]
    if res_src.findings:
        assert res_src.findings[0].status == "SOURCE_REVIEW"
        assert "enforce-safe-html.mjs" in res_src.findings[0].description

    res_cfg = await check_security_configuration(local_context)
    assert res_cfg.check_id == "CONFIG-002"
    assert res_cfg.status == CheckStatus.PASS.value

    res_dep = await check_dependency_manifests(local_context)
    assert res_dep.check_id == "DEP-001"
    assert res_dep.status == CheckStatus.PASS.value

    res_ssrf = await check_ssrf_defenses(local_context)
    assert res_ssrf.check_id == "SSRF-001"
    assert res_ssrf.status == CheckStatus.PASS.value

    res_tauri = await check_tauri_desktop_security(local_context)
    assert res_tauri.check_id == "TAURI-001"
    assert res_tauri.status == CheckStatus.PASS.value


@pytest.mark.anyio
async def test_manual_checklist_checks(local_context):
    """Verify manual verification checklist modules return MANUAL status with guidance."""
    res_auth = await check_authentication_architecture(local_context)
    assert res_auth.check_id == "AUTH-001"
    assert res_auth.status == CheckStatus.MANUAL.value

    res_authz = await check_authorization_boundaries(local_context)
    assert res_authz.check_id == "AUTHZ-001"
    assert res_authz.status == CheckStatus.MANUAL.value

    res_rate = await check_rate_limiting_policy(local_context)
    assert res_rate.check_id == "API-004"
    assert res_rate.status == CheckStatus.MANUAL.value
