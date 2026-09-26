"""Tests for evidence sanitization and secret redaction."""

from app.scanner.evidence import (
    redact_secrets,
    sanitize_cookie_header,
    sanitize_headers,
    create_evidence,
)
from app.scanner.models import EvidenceType


def test_redact_secrets_bearer_token():
    """Verify Bearer tokens are redacted."""
    raw = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.doNotLeakThis"
    sanitized = redact_secrets(raw)
    assert "doNotLeakThis" not in sanitized
    assert "[REDACTED_BEARER_TOKEN]" in sanitized


def test_redact_secrets_api_keys():
    """Verify user API keys and generic API keys are redacted."""
    raw_wm = "User key is wm_0123456789abcdef0123456789abcdef01234567"
    sanitized_wm = redact_secrets(raw_wm)
    assert "0123456789abcdef" not in sanitized_wm
    assert "[REDACTED_USER_API_KEY]" in sanitized_wm

    raw_session = "Session token: wms_eyJpYXQiOjE3MTYwMDB9.somerandomsignaturehere"
    sanitized_session = redact_secrets(raw_session)
    assert "somerandomsignaturehere" not in sanitized_session
    assert "[REDACTED_SESSION_TOKEN]" in sanitized_session


def test_sanitize_cookie_header():
    """Verify cookie values are masked while security attributes remain visible."""
    raw_cookie = "session_id=super_secret_session_data_12345; Path=/; Secure; HttpOnly; SameSite=Lax"
    sanitized = sanitize_cookie_header(raw_cookie)
    assert "super_secret_session_data_12345" not in sanitized
    assert "session_id=[REDACTED_VALUE]" in sanitized
    assert "Secure" in sanitized
    assert "HttpOnly" in sanitized
    assert "SameSite=Lax" in sanitized


def test_sanitize_headers_map():
    """Verify sensitive headers are stripped or sanitized."""
    headers = {
        "Authorization": "Bearer secret_token_xyz123",
        "X-Api-Key": "my_super_api_key_456",
        "Set-Cookie": "token=abc123456; HttpOnly",
        "Content-Type": "application/json",
    }
    sanitized = sanitize_headers(headers)
    assert sanitized["Authorization"] == "[REDACTED_AUTHORIZATION]"
    assert sanitized["X-Api-Key"] == "[REDACTED_X_API_KEY]"
    assert "abc123456" not in sanitized["Set-Cookie"]
    assert sanitized["Content-Type"] == "application/json"


def test_create_evidence_auto_redaction():
    """Verify create_evidence automatically redacts sensitive data in all fields."""
    ev = create_evidence(
        evidence_type=EvidenceType.HTTP_RESPONSE,
        title="Test Response",
        description="password='leaked_plain_password_123'",
        response_data="User wm_abcdef0123456789abcdef0123456789abcdef01 connected",
    )
    assert ev.redacted is True
    assert "leaked_plain_password_123" not in ev.description
    assert "[REDACTED_PASSWORD]" in ev.description
    assert "abcdef0123456789" not in ev.response_data
    assert "[REDACTED_USER_API_KEY]" in ev.response_data
