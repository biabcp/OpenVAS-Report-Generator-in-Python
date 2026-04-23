from __future__ import annotations

import base64
import logging
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Final

from .config import OpenVASConfig

LOGGER: Final = logging.getLogger(__name__)


class OpenVASError(RuntimeError):
    """Raised when OpenVAS operations fail."""


@dataclass
class _HttpResponse:
    status_code: int
    text: str


class OpenVASClient:
    """Client wrapper for OpenVAS OMP/GMP XML commands over HTTPS."""

    def __init__(self, config: OpenVASConfig) -> None:
        self._config = config
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, config.api_url, config.username, config.password)
        auth_handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        self._opener = urllib.request.build_opener(auth_handler)

        self._ssl_context = ssl.create_default_context()
        if not config.verify_tls:
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

    def get_report_formats(self) -> list[dict[str, str]]:
        root = self._execute("<get_report_formats/>")
        formats: list[dict[str, str]] = []
        for item in root.findall("report_format"):
            format_id = item.get("id", "")
            name = item.findtext("name", default="")
            extension = item.findtext("extension", default="")
            if format_id and name:
                formats.append({"id": format_id, "name": name, "extension": extension})
        return formats

    def start_report(self, task_id: str, report_format_id: str) -> str:
        payload = (
            f'<get_reports report_format_id="{report_format_id}" task_id="{task_id}" '
            'ignore_pagination="1" details="1"/>'
        )
        root = self._execute(payload)
        report = root.find("report")
        if report is None:
            raise OpenVASError("No report metadata returned for task")
        report_id = report.get("id", "")
        if not report_id:
            raise OpenVASError("Report response missing report id")
        return report_id

    def wait_for_report(self, report_id: str) -> None:
        for attempt in range(1, self._config.max_poll_attempts + 1):
            payload = f'<get_report report_id="{report_id}" details="0"/>'
            root = self._execute(payload)
            status = root.findtext("report/report/status", default="").lower()
            LOGGER.info("Polling report %s, attempt %s, status=%s", report_id, attempt, status)
            if status in {"done", "finished"}:
                return
            if status in {"stopped", "interrupted", "error", "failed"}:
                raise OpenVASError(f"Report generation failed with status: {status}")
            time.sleep(self._config.poll_interval_seconds)
        raise OpenVASError("Timed out waiting for report completion")

    def download_report(self, report_id: str, report_format_id: str) -> bytes:
        payload = (
            f'<get_reports report_id="{report_id}" report_format_id="{report_format_id}" '
            'details="1" ignore_pagination="1"/>'
        )
        root = self._execute(payload)
        content = root.findtext("report/report", default="").strip()
        if not content:
            raise OpenVASError("Report content missing from response")

        try:
            return base64.b64decode(content, validate=True)
        except (ValueError, base64.binascii.Error):
            return content.encode("utf-8")

    def _post(self, endpoint: str, data: dict[str, str]) -> _HttpResponse:
        encoded = urllib.parse.urlencode(data).encode("utf-8")
        request = urllib.request.Request(endpoint, data=encoded, method="POST")
        try:
            with self._opener.open(
                request,
                timeout=self._config.timeout_seconds,
                context=self._ssl_context,
            ) as response:
                body = response.read().decode("utf-8", errors="replace")
                return _HttpResponse(status_code=getattr(response, "status", 200), text=body)
        except urllib.error.HTTPError as exc:
            text = exc.read().decode("utf-8", errors="replace")
            return _HttpResponse(status_code=exc.code, text=text)
        except urllib.error.URLError as exc:
            raise OpenVASError(f"Unable to connect to OpenVAS endpoint: {exc.reason}") from exc

    def _execute(self, xml_command: str) -> ET.Element:
        endpoint = f"{self._config.api_url.rstrip('/')}/omp"
        response = self._post(endpoint, {"cmd": xml_command})
        if response.status_code >= 400:
            raise OpenVASError(
                f"OpenVAS API returned HTTP {response.status_code}: {response.text[:200]}"
            )

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as exc:
            raise OpenVASError(f"Failed to parse XML response: {exc}") from exc

        status = root.get("status")
        if status is not None and not status.startswith("2"):
            status_text = root.get("status_text", "unknown error")
            raise OpenVASError(f"OpenVAS command failed: {status} {status_text}")

        return root
