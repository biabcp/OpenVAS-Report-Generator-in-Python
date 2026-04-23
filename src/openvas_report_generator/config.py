from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OpenVASConfig:
    """Runtime configuration for connecting to the OpenVAS API."""

    api_url: str
    username: str
    password: str
    verify_tls: bool = True
    timeout_seconds: int = 30
    poll_interval_seconds: int = 5
    max_poll_attempts: int = 120

    @classmethod
    def from_env(cls) -> "OpenVASConfig":
        """Build config from environment variables."""
        api_url = os.getenv("OPENVAS_API_URL", "").strip()
        username = os.getenv("OPENVAS_USERNAME", "").strip()
        password = os.getenv("OPENVAS_PASSWORD", "").strip()

        if not api_url:
            raise ValueError("OPENVAS_API_URL is required")
        if not username:
            raise ValueError("OPENVAS_USERNAME is required")
        if not password:
            raise ValueError("OPENVAS_PASSWORD is required")

        verify_tls = os.getenv("OPENVAS_VERIFY_TLS", "true").lower() in {"1", "true", "yes"}
        timeout_seconds = int(os.getenv("OPENVAS_TIMEOUT_SECONDS", "30"))
        poll_interval_seconds = int(os.getenv("OPENVAS_POLL_INTERVAL_SECONDS", "5"))
        max_poll_attempts = int(os.getenv("OPENVAS_MAX_POLL_ATTEMPTS", "120"))

        return cls(
            api_url=api_url,
            username=username,
            password=password,
            verify_tls=verify_tls,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            max_poll_attempts=max_poll_attempts,
        )
