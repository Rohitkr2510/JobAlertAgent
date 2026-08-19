# ReleaseGuard

ReleaseGuard is an offline, policy-driven release-readiness agent. It scans a repository,
applies deterministic quality and security rules, calculates a readiness score, and returns
`PASS`, `WARNING`, or `BLOCKED`. It does not use OpenAI, Claude, Gemini, or any external LLM.

## Current checks

- Required release artifacts such as a changelog and rollback plan
- Common credentials accidentally committed to text files
- Docker non-root user, health check, and mutable `latest` base images
- Oversized repository files
- YAML-defined scoring and promotion threshold
- JSON and standalone HTML evidence reports

## Quick start with Docker

Build the image:

```bash
docker build -t releaseguard:local .
```

Scan the current repository. The target is mounted read-only:

```bash
docker run --rm \
  -v "$PWD:/workspace:ro" \
  -v "$PWD/reports:/reports" \
  releaseguard:local scan /workspace \
  --policy /app/release-policy.yaml \
  --output /reports
```

Exit codes are designed for CI/CD gates:

| Code | Meaning |
|---:|---|
| 0 | Passed |
| 1 | Passed with warnings |
| 2 | Blocked by policy |
| 3 | Configuration or execution error |

## Run the local API

```bash
docker compose up --build
curl http://localhost:8080/health
curl -X POST http://localhost:8080/v1/scan \
  -H 'Content-Type: application/json' \
  -d '{"path":"/workspace","policy":"/app/release-policy.yaml"}'
```

Interactive API documentation is available at `http://localhost:8080/docs`.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
ruff check .
releaseguard scan . --policy release-policy.yaml
```

## Configure the gate

Edit `release-policy.yaml` to change the minimum score, mandatory artifacts, Docker rules,
file-size threshold, and category weights. ReleaseGuard reads the policy at scan time, so
no image rebuild is needed when the file is mounted into the container.

## Security model

- Repository mounts should be read-only.
- The service runs as a non-root user.
- Docker Compose drops Linux capabilities and prevents privilege escalation.
- ReleaseGuard does not require access to the Docker socket.
- Reports include file paths and findings, never the detected secret value.

## Roadmap

- Optional offline adapters for Trivy, Gitleaks, Hadolint, Semgrep and Kubeconform
- Terraform validation and OPA/Rego policies
- Signed audit-evidence bundles
- Baseline comparison and approved exceptions
- Jenkins shared-library integration

## License

MIT
