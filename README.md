# JobAlertAgent

JobAlertAgent is a local, Docker-ready automation that reads job-alert emails from Gmail or exported `.eml` files, extracts job links, applies deterministic DevOps/experience/recency filters, removes duplicates, stores history in SQLite, and creates a prioritized Excel workbook. It uses no LLM and no paid API.

## What it does

- Supports LinkedIn, Indeed, and Naukri alert emails
- Searches Gmail messages received in the last 24 hours
- Filters DevOps, SRE, cloud, platform, CI/CD, and infrastructure roles
- Scores skills and experience for an approximately 2.7-year profile
- Generates High Priority, Medium Priority, Needs Review, All Jobs, and Run Summary sheets
- Keeps OAuth tokens, credentials, mail, database, and reports outside the image

## Offline demo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
jobalert collect-eml tests/fixtures --config config/job-filters.yaml --output reports
```

## Gmail setup (free)

1. Create a Google Cloud project and enable the Gmail API.
2. Create an OAuth Desktop App and download it as `secrets/credentials.json`.
3. Run `jobalert gmail-auth --credentials secrets/credentials.json --token secrets/token.json` once on a machine with a browser.
4. Run the collector:

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
docker compose run --rm jobalert collect-gmail \
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
