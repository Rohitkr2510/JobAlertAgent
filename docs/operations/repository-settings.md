# Enterprise repository settings

These controls require repository-administrator configuration and cannot be enforced by files alone.

## Protect `main`

- Require a pull request before merging.
- Require at least one approval and dismiss stale approvals.
- Require conversation resolution.
- Require branches to be up to date.
- Require `quality`, `container-smoke`, `monitoring-config`, `python-security`, `secrets`, `container-security`, `codeql`, and `validate` checks.
- Block force pushes and deletion.
- Restrict bypass permission to emergency administrators.
- Prefer squash merge for a linear, auditable history.

## Protect releases

- Create a `production` environment.
- Add a required reviewer and prevent self-review where the plan supports it.
- Restrict deployments to tags matching `v*`.
- Keep workflow permissions read-only by default; grant write permissions only at the release job.
- Disable tag deletion or replacement through organizational policy where available.

## Supply-chain maturity

- Pin third-party actions to reviewed immutable commit SHAs and record the upstream version in comments.
- Review grouped Dependabot updates weekly.
- Verify SBOM, provenance, and Cosign identity before deployment.
- Deploy GHCR images by digest.
- Enable private vulnerability reporting and secret-scanning push protection where available.

## Ownership

`CODEOWNERS` identifies review owners but is enforceable only when branch protection requires code-owner review. At least two maintainers are recommended before treating the service as organization-critical.
