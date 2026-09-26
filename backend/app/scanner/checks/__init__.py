"""Security assessment check implementations."""

from app.scanner.checks.headers import check_security_headers
from app.scanner.checks.cors import check_cors_policy
from app.scanner.checks.cookies import check_cookie_security
from app.scanner.checks.tls import check_tls_configuration
from app.scanner.checks.information_disclosure import check_information_disclosure
from app.scanner.checks.source_security import check_source_security_patterns
from app.scanner.checks.configuration import check_security_configuration
from app.scanner.checks.dependency_security import check_dependency_manifests
from app.scanner.checks.api_discovery import check_api_discovery
from app.scanner.checks.rate_limiting import check_rate_limiting_policy
from app.scanner.checks.authentication import check_authentication_architecture
from app.scanner.checks.authorization import check_authorization_boundaries
from app.scanner.checks.ssrf import check_ssrf_defenses
from app.scanner.checks.tauri import check_tauri_desktop_security

__all__ = [
    "check_security_headers",
    "check_cors_policy",
    "check_cookie_security",
    "check_tls_configuration",
    "check_information_disclosure",
    "check_source_security_patterns",
    "check_security_configuration",
    "check_dependency_manifests",
    "check_api_discovery",
    "check_rate_limiting_policy",
    "check_authentication_architecture",
    "check_authorization_boundaries",
    "check_ssrf_defenses",
    "check_tauri_desktop_security",
]
