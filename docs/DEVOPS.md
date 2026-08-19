# DevOps operations guide

## Quality gates

GitHub Actions validates Python 3.14, formatting, linting, typing, coverage, packages, containers, UI health, operations endpoints, monitoring configuration, secrets, dependencies, source security, Dockerfiles, CodeQL, and container vulnerabilities.

No real Gmail token is used in CI. OAuth and Gmail responses are mocked; production authorization happens only through the local dashboard.

## Local services

```bash
docker compose -f compose.yaml -f compose.monitoring.yaml up --build -d
```

| Service | URL |
|---|---|
| JobAlertAgent | http://localhost:8501 |
| Operations API | http://localhost:8080 |
| Liveness | http://localhost:8080/health/live |
| Readiness | http://localhost:8080/health/ready |
| Metrics | http://localhost:8080/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Alertmanager | http://localhost:9093 |
| Loki | http://localhost:3100 |

Change `GRAFANA_ADMIN_PASSWORD` before using the monitoring stack outside an isolated development machine.

## Release process

1. Ensure CI Quality Gate and DevSecOps are green.
2. Create a semantic version tag such as `v0.3.0`.
3. The release workflow builds AMD64 and ARM64 images.
4. The image is published to `ghcr.io/rohitkr2510/job-alert-agent`.
5. GitHub creates provenance, an SPDX SBOM, a keyless Sigstore signature, and a GitHub Release.
6. Configure a protected `production` GitHub Environment to require approval.

## GitHub-only evidence

The Actions page exposes logs, coverage, packages, SBOMs, build records, CodeQL results, Trivy SARIF, attestations, releases, and container packages. A local clone is not required to review this evidence.

Repository administrators should also apply the [enterprise repository settings](operations/repository-settings.md) before the first production release.
