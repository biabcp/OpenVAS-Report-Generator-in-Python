import os
import unittest
from unittest.mock import patch

from openvas_report_generator.config import OpenVASConfig


class TestOpenVASConfig(unittest.TestCase):
    def test_from_env_success(self) -> None:
        env = {
            "OPENVAS_API_URL": "https://scanner.example:9392",
            "OPENVAS_USERNAME": "user",
            "OPENVAS_PASSWORD": "pass",
            "OPENVAS_VERIFY_TLS": "false",
            "OPENVAS_TIMEOUT_SECONDS": "45",
        }
        with patch.dict(os.environ, env, clear=True):
            config = OpenVASConfig.from_env()

        self.assertEqual(config.api_url, env["OPENVAS_API_URL"])
        self.assertFalse(config.verify_tls)
        self.assertEqual(config.timeout_seconds, 45)

    def test_from_env_requires_values(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                OpenVASConfig.from_env()


if __name__ == "__main__":
    unittest.main()
