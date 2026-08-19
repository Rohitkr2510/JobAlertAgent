# ADR-0003: Deterministic scoring without an LLM

- Status: Accepted
- Date: 2026-08-19

## Decision

Use configuration-driven keyword, experience, location, source, and recency rules. Store an explanation with each result.

## Consequences

Processing is free, private, repeatable, and testable. Semantic matching is limited; an optional AI integration would need explicit privacy, cost, evaluation, and fallback decisions.
