"""Evidence collection and sensitive data redaction module."""

import re
from typing import Optional, Mapping
from app.scanner.models import EvidenceItem, EvidenceType

# Common secret patterns for automated redaction
SENSITIVE_PATTERNS = [
    (re.compile(r"(Bearer\s+)[A-Za-z0-9_\-\.]{15,}", re.IGNORECASE), r"\1[REDACTED_BEARER_TOKEN]"),
    (re.compile(r"(api[_\-]?key\s*[:=]\s*['\"]?)[A-Za-z0-9_\-]{16,}(['\"]?)", re.IGNORECASE), r"\1[REDACTED_API_KEY]\2"),
    (re.compile(r"(password\s*[:=]\s*['\"]?)[^\r\n'\"]{4,}(['\"]?)", re.IGNORECASE), r"\1[REDACTED_PASSWORD]\2"),
    (re.compile(r"(secret\s*[:=]\s*['\"]?)[A-Za-z0-9_\-]{8,}(['\"]?)", re.IGNORECASE), r"\1[REDACTED_SECRET]\2"),
    (re.compile(r"(wms_[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+)", re.IGNORECASE), r"[REDACTED_SESSION_TOKEN]"),
    (re.compile(r"(wm_[a-f0-9]{40})", re.IGNORECASE), r"[REDACTED_USER_API_KEY]"),
    (re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----"), r"[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82})"), r"[REDACTED_GITHUB_TOKEN]"),
]

SENSITIVE_HEADER_NAMES = {
    "authorization",
    "x-api-key",
    "x-worldmonitor-key",
    "x-worldmonitor-local-token",
    "cookie",
    "proxy-authorization",
}


def redact_secrets(text: Optional[str]) -> Optional[str]:
    """Redact sensitive credentials, tokens, and secret patterns from strings."""
    if not text:
        return text

    sanitized = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)

    return sanitized


def sanitize_cookie_header(cookie_header: str) -> str:
    """Sanitize Set-Cookie header by masking cookie value while keeping security attributes."""
    parts = cookie_header.split(";")
    if not parts:
        return cookie_header

    first_part = parts[0].strip()
    if "=" in first_part:
        name, _ = first_part.split("=", 1)
        sanitized_first = f"{name}=[REDACTED_VALUE]"
    else:
        sanitized_first = "[REDACTED_COOKIE]"

    attrs = [p.strip() for p in parts[1:]]
    if attrs:
        return f"{sanitized_first}; {'; '.join(attrs)}"
    return sanitized_first


def sanitize_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Sanitize an HTTP headers map to strip plaintext secrets and credentials."""
    sanitized: dict[str, str] = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if key_lower in SENSITIVE_HEADER_NAMES:
            sanitized[key] = f"[REDACTED_{key.upper().replace('-', '_')}]"
        elif key_lower == "set-cookie":
            sanitized[key] = sanitize_cookie_header(value)
        else:
            sanitized[key] = redact_secrets(value) or ""
    return sanitized


def create_evidence(
    evidence_type: EvidenceType,
    title: str,
    description: Optional[str] = None,
    request_data: Optional[str] = None,
    response_data: Optional[str] = None,
    source_file: Optional[str] = None,
    source_line: Optional[int] = None,
) -> EvidenceItem:
    """Construct an EvidenceItem with mandatory automatic redaction."""
    return EvidenceItem(
        evidence_type=evidence_type.value,
        title=title,
        description=redact_secrets(description),
        request_data=redact_secrets(request_data),
        response_data=redact_secrets(response_data),
        source_file=source_file,
        source_line=source_line,
        redacted=True,
    )
