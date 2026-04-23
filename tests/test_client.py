import base64
import unittest
from unittest.mock import Mock

from openvas_report_generator.client import OpenVASClient, _HttpResponse
from openvas_report_generator.config import OpenVASConfig


class TestOpenVASClient(unittest.TestCase):
    def _client(self) -> OpenVASClient:
        cfg = OpenVASConfig(
            api_url="https://scanner.example:9392",
            username="user",
            password="pass",
            max_poll_attempts=1,
            poll_interval_seconds=0,
        )
        return OpenVASClient(cfg)

    def test_get_report_formats(self) -> None:
        client = self._client()
        client._post = Mock(return_value=_HttpResponse(status_code=200, text=(
            "<get_report_formats_response status='200' status_text='OK'>"
            "<report_format id='a1'><name>PDF</name><extension>pdf</extension></report_format>"
            "</get_report_formats_response>"
        )))  # type: ignore[method-assign]

        formats = client.get_report_formats()

        self.assertEqual(formats[0]["id"], "a1")
        self.assertEqual(formats[0]["name"], "PDF")

    def test_download_report_base64(self) -> None:
        client = self._client()
        encoded = base64.b64encode(b"report-bytes").decode()
        client._post = Mock(return_value=_HttpResponse(status_code=200, text=(
            "<get_reports_response status='200' status_text='OK'>"
            "<report><report>" + encoded + "</report></report>"
            "</get_reports_response>"
        )))  # type: ignore[method-assign]

        data = client.download_report("r1", "f1")

        self.assertEqual(data, b"report-bytes")


if __name__ == "__main__":
    unittest.main()
