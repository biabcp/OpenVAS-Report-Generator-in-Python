from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .client import OpenVASClient, OpenVASError
from .config import OpenVASConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate OpenVAS reports from task scans")
    parser.add_argument("--task-id", required=True, help="OpenVAS task ID")
    parser.add_argument("--report-format-id", required=True, help="OpenVAS report format ID")
    parser.add_argument(
        "--output",
        default="scan_reports/scan_report.out",
        help="Output path (default: scan_reports/scan_report.out)",
    )
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    try:
        config = OpenVASConfig.from_env()
        client = OpenVASClient(config)
        report_id = client.start_report(task_id=args.task_id, report_format_id=args.report_format_id)
        client.wait_for_report(report_id)
        report_data = client.download_report(
            report_id=report_id,
            report_format_id=args.report_format_id,
        )

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(report_data)
        logging.info("Report written to %s", output_path)
        return 0
    except (ValueError, OpenVASError) as exc:
        logging.error("Failed to generate report: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
