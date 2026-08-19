# ADR-0001: Offline-first SQLite architecture

- Status: Accepted
- Date: 2026-08-19

## Context

The initial product is a personal automation that must keep job and email-derived data under the operator's control without paid infrastructure.

## Decision

Use local SQLite and mounted report storage. Design for one primary host and one writer process group.

## Consequences

Deployment is free, portable, and private. Horizontal scaling, concurrent remote users, high availability, and online schema changes are outside the current boundary and require a future database ADR.
