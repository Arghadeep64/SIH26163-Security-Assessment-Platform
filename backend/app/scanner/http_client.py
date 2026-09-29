"""Defensive, bounded HTTP client for security assessment checks."""

import time
from dataclasses import dataclass
from typing import Optional, Mapping
import httpx

from app.scanner.context import ScanContext
from app.scanner.evidence import sanitize_headers, redact_secrets

ALLOWED_HTTP_METHODS = {"GET", "HEAD", "OPTIONS"}
PROHIBITED_HOSTS = {"worldmonitor.app", "www.worldmonitor.app", "api.worldmonitor.app"}


@dataclass
class SafeHttpResponse:
    """Bounded, safe representation of an HTTP response."""

    status_code: int
    headers: dict[str, str]
    body: str
    duration_ms: float
    url: str
    method: str
    is_success: bool
    is_redirect: bool
    error: Optional[str] = None


class SafeHttpClient:
    """Safe HTTP client executing bounded, defensive requests against authorized targets."""

    def __init__(self, context: ScanContext):
        self.context = context
        self._validate_target_safety()

    def _validate_target_safety(self) -> None:
        """Enforce that scanner only executes against authorized targets and never against production."""
        if not self.context.authorized:
            raise PermissionError("ScanContext must be explicitly authorized to execute network checks.")

        target_lower = self.context.target_url.lower()
        for prohibited in PROHIBITED_HOSTS:
            if prohibited in target_lower and not self.context.is_local_target():
                raise PermissionError(
                    f"Automated scanning against production target '{prohibited}' is prohibited by SIH26163 policy."
                )

    async def request(
        self,
        method: str,
        path: str = "",
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> SafeHttpResponse:
        """Execute a safe HTTP request with strict bounds."""
        method_upper = method.strip().upper()
        if method_upper not in ALLOWED_HTTP_METHODS:
            raise ValueError(f"Method '{method_upper}' is not in allowed safe assessment methods: {ALLOWED_HTTP_METHODS}")

        base_url = self.context.target_url.rstrip("/")
        normalized_path = "/" + path.lstrip("/") if path else ""
        full_url = f"{base_url}{normalized_path}"

        req_headers = {
            "User-Agent": self.context.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            **(dict(headers) if headers else {}),
        }

        req_timeout = timeout if timeout is not None else float(self.context.timeout)
        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(req_timeout),
                follow_redirects=True,
                max_redirects=self.context.max_redirects,
                verify=True,
            ) as client:
                resp = await client.request(
                    method=method_upper,
                    url=full_url,
                    headers=req_headers,
                )
                duration_ms = (time.perf_counter() - start_time) * 1000.0

                # Truncate response body if it exceeds bounds
                content_bytes = resp.content[: self.context.max_response_bytes]
                try:
                    text_body = content_bytes.decode("utf-8", errors="replace")
                except Exception:
                    text_body = "[Binary response content truncated]"

                sanitized_resp_headers = sanitize_headers(resp.headers)

                return SafeHttpResponse(
                    status_code=resp.status_code,
                    headers=sanitized_resp_headers,
                    body=redact_secrets(text_body) or "",
                    duration_ms=duration_ms,
                    url=full_url,
                    method=method_upper,
                    is_success=resp.is_success,
                    is_redirect=resp.is_redirect,
                    error=None,
                )

        except httpx.RequestError as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return SafeHttpResponse(
                status_code=0,
                headers={},
                body="",
                duration_ms=duration_ms,
                url=full_url,
                method=method_upper,
                is_success=False,
                is_redirect=False,
                error=f"Network connection failed: {exc.__class__.__name__} ({str(exc)})",
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return SafeHttpResponse(
                status_code=0,
                headers={},
                body="",
                duration_ms=duration_ms,
                url=full_url,
                method=method_upper,
                is_success=False,
                is_redirect=False,
                error=f"Unexpected error during safe request: {str(exc)}",
            )
