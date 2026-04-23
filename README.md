# OpenVAS Report Generator (Python)

Production-oriented CLI for generating OpenVAS/GVM reports with safer defaults, configuration via environment variables, and test coverage.

## What changed

- Converted a single script into an installable Python package.
- Added a command-line interface (`openvas-report`).
- Added stricter configuration validation.
- Added structured logging and polling controls.
- Added unit tests for core configuration/client behavior.

## Project layout

- `src/openvas_report_generator/config.py` – runtime configuration and env parsing.
- `src/openvas_report_generator/client.py` – OpenVAS API client.
- `src/openvas_report_generator/cli.py` – CLI entrypoint.
- `tests/` – unit tests.

## Quick start

### 1) Install

```bash
python -m pip install -e .
```

### 2) Configure environment

```bash
export OPENVAS_API_URL="https://your-openvas-server:9392"
export OPENVAS_USERNAME="your-username"
export OPENVAS_PASSWORD="your-password"
# Optional overrides:
# export OPENVAS_VERIFY_TLS="true"
# export OPENVAS_TIMEOUT_SECONDS="30"
# export OPENVAS_POLL_INTERVAL_SECONDS="5"
# export OPENVAS_MAX_POLL_ATTEMPTS="120"
```

### 3) Generate a report

```bash
openvas-report \
  --task-id "<task-id>" \
  --report-format-id "<report-format-id>" \
  --output "scan_reports/scan_report.pdf"
```

## Notes for production use

- Keep TLS verification enabled (`OPENVAS_VERIFY_TLS=true`) and trust your CA chain.
- Inject credentials through a secret manager or CI/CD secret store.
- Run this CLI from a restricted service account.
- Add integration tests against a non-production OpenVAS instance.

## License

MIT (add a `LICENSE` file if your organization requires one explicitly in-repo).
