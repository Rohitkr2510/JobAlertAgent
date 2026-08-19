# ADR-0004: Signed GHCR container releases

- Status: Accepted
- Date: 2026-08-19

## Decision

Publish AMD64 and ARM64 images to GHCR by immutable digest, generate an SPDX SBOM, create GitHub provenance, and sign keylessly with Sigstore OIDC.

## Consequences

Consumers can verify origin without a long-lived signing key. Releases depend on GitHub and Sigstore availability and require protected environment approval.
