"""Security check registry managing check definitions and execution order."""

from typing import Callable, Awaitable
from app.scanner.context import ScanContext
from app.scanner.models import CheckResult
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

CheckFunction = Callable[[ScanContext], Awaitable[CheckResult]]

CHECK_REGISTRY: list[CheckFunction] = [
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
]


def get_registered_checks() -> list[CheckFunction]:
    """Retrieve all active registered security checks."""
    return list(CHECK_REGISTRY)


def register_check(check_fn: CheckFunction) -> None:
    """Register a new security check function."""
    if check_fn not in CHECK_REGISTRY:
        CHECK_REGISTRY.append(check_fn)
