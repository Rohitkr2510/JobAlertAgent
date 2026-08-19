# Testing strategy

## Test layers

| Layer | Evidence |
|---|---|
| Unit | Parser, scoring, storage, encryption, and account behavior |
| Integration | Synchronization success/failure, reports, health, readiness, and metrics |
| Functional | Offline self-check from message parsing through encrypted token round-trip |
| Container | Image build, Streamlit health, operations API, and Compose validation |
| Security | Bandit, pip-audit, Gitleaks, Hadolint, Trivy, and CodeQL |
| Documentation | Required files, links, Mermaid blocks, and prohibited personal data |

Coverage must remain at or above the configured threshold. Coverage is supporting evidence, not a replacement for assertions about failure behavior and data protection.

Tests must be deterministic, must not call Gmail, and must not depend on a real user account. OAuth and Gmail responses are mocked.
