from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from app.config import PROJECT_ROOT


@dataclass
class ScanContext:
    """Encapsulates execution parameters, target metadata, and safety guards for an assessment."""

    assessment_id: int
    target_url: str = "http://localhost:3000"
    target_type: str = "LOCAL"  # LOCAL, AUTHORIZED_REMOTE, DEMO
    timeout: int = 10
    authorized: bool = True
    source_path: str = "research/worldmonitor"
    max_redirects: int = 3
    max_response_bytes: int = 1024 * 1024  # 1 MB maximum response payload
    user_agent: str = "SIH26163-Security-Assessment-Bot/1.0"
    client_cert: Optional[str] = None

    def __post_init__(self) -> None:
        """Resolve source_path against PROJECT_ROOT if relative."""
        p = Path(self.source_path)
        if not p.is_absolute():
            candidate = (PROJECT_ROOT / p).resolve()
            if candidate.exists() or not p.exists():
                self.source_path = str(candidate)

    def is_local_target(self) -> bool:
        """Determine if target URL points to a local loopback address."""
        url_lower = self.target_url.lower()
        return "localhost" in url_lower or "127.0.0.1" in url_lower or "0.0.0.0" in url_lower

    def is_demo_target(self) -> bool:
        """Determine if target is a controlled demo environment."""
        url_lower = self.target_url.lower()
        return self.target_type == "DEMO" or ":9000" in url_lower or "demo-target" in url_lower

    def get_finding_prefix(self) -> str:
        """Return standardized prefix for findings depending on target classification."""
        if self.is_demo_target():
            return "[CONTROLLED DEMO FINDING — NOT A WORLDMONITOR FINDING] "
        return ""

