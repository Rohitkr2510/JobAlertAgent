# ADR-0002: Gmail API with read-only OAuth

- Status: Accepted
- Date: 2026-08-19

## Decision

Use the official Gmail API and the narrow read-only scope. Never accept Gmail passwords or enable message mutation.

## Consequences

Google consent and client configuration are required, but authorization is revocable, auditable, multi-account capable, and safer than stored passwords or broad mailbox permissions.
