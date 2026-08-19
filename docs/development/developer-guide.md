# Developer guide

## Prerequisites

- Python 3.14
- Git
- Docker with Compose for container and monitoring validation

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev,gmail,ui,ops]'
```

## Quality commands

```bash
ruff check .
ruff format --check .
mypy src/jobalert
pytest --cov=jobalert --cov-report=term-missing
bandit -c pyproject.toml -r src
pip-audit
jobalert self-check
```

## Adding a source parser

1. Add a representative, anonymized message fixture.
2. Extract stable job fields without executing email content.
3. Normalize tracked redirect URLs.
4. Add positive, malformed, duplicate, and old-message tests.
5. Update supported-source documentation and scoring explanations.

Never add real email addresses, OAuth files, message exports, databases, or generated reports to fixtures.
