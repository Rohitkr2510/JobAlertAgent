# Release process

## Preconditions

- Documentation and code changes are merged through reviewed pull requests.
- CI Quality Gate, DevSecOps, and documentation validation are green on `main`.
- `production` is a protected GitHub Environment with an approver.
- The version in `pyproject.toml` and `src/jobalert/__init__.py` matches the tag.
- The release checklist is completed.

## Publish

1. Create an annotated semantic-version tag from the reviewed `main` commit.
2. Push the tag or manually dispatch the release workflow with that existing tag.
3. Approve the protected production job.
4. Verify the multi-architecture image, SPDX SBOM, provenance attestation, and keyless signature.
5. Publish release notes with breaking changes, migration guidance, and known limitations.

## Verify

```bash
cosign verify ghcr.io/rohitkr2510/job-alert-agent@sha256:DIGEST \
  --certificate-identity-regexp 'github.com/Rohitkr2510/JobAlertAgent' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

Deploy by immutable digest, never by a mutable tag alone.

## Rollback

Redeploy the last verified digest. Do not delete a bad release or overwrite its tag; mark it as affected, document the reason, and publish a corrected patch version.
