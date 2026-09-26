"""Severity classification helpers and evaluation utilities."""

from typing import Optional
from app.scanner.models import SeverityLevel


SEVERITY_RANKS = {
    SeverityLevel.INFO.value: 1,
    SeverityLevel.LOW.value: 2,
    SeverityLevel.MEDIUM.value: 3,
    SeverityLevel.HIGH.value: 4,
    SeverityLevel.CRITICAL.value: 5,
}


def normalize_severity(val: Optional[str]) -> str:
    """Validate and normalize a severity string."""
    if not val:
        return SeverityLevel.INFO.value
    val_upper = val.strip().upper()
    if val_upper in SEVERITY_RANKS:
        return val_upper
    return SeverityLevel.INFO.value


def get_severity_rank(severity: str) -> int:
    """Return numeric rank for comparative severity sorting."""
    return SEVERITY_RANKS.get(normalize_severity(severity), 1)


def compare_severity(sev1: str, sev2: str) -> int:
    """Compare two severity levels (-1 if sev1 < sev2, 0 if equal, 1 if sev1 > sev2)."""
    r1 = get_severity_rank(sev1)
    r2 = get_severity_rank(sev2)
    if r1 < r2:
        return -1
    if r1 > r2:
        return 1
    return 0
