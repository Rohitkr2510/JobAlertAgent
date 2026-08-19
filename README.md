# JobAlertAgent

[![Validate JobAlertAgent](https://github.com/Rohitkr2510/JobAlertAgent/actions/workflows/ci.yml/badge.svg)](https://github.com/Rohitkr2510/JobAlertAgent/actions/workflows/ci.yml)
[![DevSecOps](https://github.com/Rohitkr2510/JobAlertAgent/actions/workflows/security.yml/badge.svg)](https://github.com/Rohitkr2510/JobAlertAgent/actions/workflows/security.yml)

JobAlertAgent is a local, Docker-ready multi-account Gmail automation and Streamlit dashboard. It extracts job alerts, applies deterministic DevOps/experience/recency filters, removes duplicates, tracks applications, schedules daily scans, and creates prioritized Excel workbooks. It uses no LLM and no paid API.

## What it does

- Supports LinkedIn, Indeed, and Naukri alert emails
- Searches Gmail messages received in the last 24 hours
- Filters DevOps, SRE, cloud, platform, CI/CD, and infrastructure roles
- Scores skills and experience for an approximately 2.7-year profile
- Generates High Priority, Medium Priority, Needs Review, All Jobs, and Run Summary sheets
- Keeps OAuth tokens, credentials, mail, database, and reports outside the image
- Encrypts a separate OAuth token for every connected Gmail account
- Provides a local dashboard, application tracker, filters, logs, scheduling, and reports
- Validates itself in GitHub Actions with tests, package build, Docker build, and UI health check
- Publishes signed, attested multi-platform releases with an SPDX SBOM to GHCR
- Exposes health, readiness and Prometheus metrics with Grafana, Loki and Alertmanager

## Dashboard

```bash
pip install -e '.[gmail,ui]'
streamlit run src/jobalert/ui.py
```

Open `http://localhost:8501`. For UI-based Gmail connection, create a Google OAuth **Web application** client with `http://localhost:8501` as an authorized redirect URI, then save it as `secrets/web_credentials.json`.

With Docker:

```bash
docker compose up --build
```

## Validation without cloning

Open the repository's **Actions** tab. Every push automatically runs:

- Python 3.14 runtime validation
- Ruff, mypy, coverage, Bandit, pip-audit, Gitleaks, Hadolint, Trivy and CodeQL
- Unit and integration tests
- Offline functional self-check
- Dashboard import test
- Python package build
- Docker image build
- Live Streamlit health-endpoint smoke test
- Operations API and monitoring configuration validation
- Signed GHCR releases with SBOM and provenance

Both `CI Quality Gate` and `DevSecOps` must be green before a release is considered ready. See the [DevOps operations guide](docs/DEVOPS.md).

## Offline demo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
jobalert collect-eml tests/fixtures --config config/job-filters.yaml --output reports
```

## Gmail setup (free)

Follow the complete [free Gmail OAuth setup guide](docs/GMAIL_SETUP.md). In short:

1. Create a Google Cloud project and enable the Gmail API.
2. Configure the OAuth audience and add your Gmail address as a test user.
3. Create an OAuth Desktop App and download it as `secrets/credentials.json`.
4. Run `jobalert gmail-auth --credentials secrets/credentials.json --token secrets/token.json` once on a machine with a browser.
5. Run the collector:

```bash
jobalert collect-gmail \
  --credentials secrets/credentials.json \
  --token secrets/token.json \
  --config config/job-filters.yaml \
  --output reports
```

OAuth uses read-only Gmail access. The first authorization needs a browser; normal scheduled runs reuse the token.

## Docker

```bash
docker compose run --rm --entrypoint jobalert jobalert collect-gmail \
  --credentials /app/secrets/credentials.json \
  --token /app/secrets/token.json \
  --config /app/config/job-filters.yaml \
  --output /app/reports
```

## Security

Never commit `credentials.json`, `token.json`, exported emails, databases, or generated reports. These paths are ignored by Git and mounted into Docker at runtime.

## Limitations

Email layouts change, so parsers may require maintenance. If a posting date is absent, the agent uses the email receipt time and marks the date as unverified. Gmail collection needs internet; parsing and report generation are local.

## License

MIT
