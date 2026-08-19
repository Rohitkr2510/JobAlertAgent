# System architecture

## Context

JobAlertAgent is an offline-first personal job-alert processor. Gmail is the only external data source. Email content, OAuth tokens, the SQLite database, and reports remain on the operator-controlled host.

```mermaid
flowchart TB
    Person["Job seeker"] --> UI["Streamlit dashboard"]
    UI --> Agent["JobAlertAgent"]
    Agent --> Gmail["Gmail API"]
    Agent --> Files["Local encrypted tokens, SQLite, reports"]
    Operator["Operator"] --> GitHub["GitHub Actions and GHCR"]
    GitHub --> Image["Signed container image"]
```

## Runtime containers

```mermaid
flowchart TB
    Browser["Browser"] --> UI["Streamlit :8501"]
    UI --> Core["Parser, scoring, scheduler"]
    Core --> Gmail["Gmail read-only API"]
    Core --> DB["SQLite volume"]
    Core --> Reports["Excel report volume"]
    Ops["FastAPI operations :8080"] --> DB
    Prom["Prometheus"] --> Ops
    Grafana["Grafana"] --> Prom
    Grafana --> Loki["Loki"]
    Alloy["Alloy"] --> Loki
    Prom --> Alerts["Alertmanager"]
```

## Email processing sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Dashboard
    participant OAuth as OAuth manager
    participant Gmail as Gmail API
    participant Sync as Sync engine
    participant DB as SQLite
    User->>UI: Connect Gmail account
    UI->>OAuth: Start authorization
    OAuth->>Gmail: Read-only consent
    Gmail-->>OAuth: Authorization code
    OAuth->>DB: Store encrypted token
    User->>UI: Start synchronization
    UI->>Sync: Sync enabled accounts
    Sync->>Gmail: Query recent alert mail
    Gmail-->>Sync: Message metadata and bodies
    Sync->>Sync: Parse, score, filter, deduplicate
    Sync->>DB: Store jobs and run result
    DB-->>UI: Dashboard data
```

## Data model

```mermaid
erDiagram
    ACCOUNTS {
        string account_id PK
        string email UK
        blob token_encrypted
        boolean enabled
        string last_sync
        string last_error
    }
    JOBS {
        string unique_id PK
        string account_email
        string title
        string company
        string url
        int score
        string priority
        string application_status
    }
    RUNS {
        int id PK
        string account_email
        string started_at
        string status
        int emails_processed
        int jobs_found
    }
    SETTINGS {
        string key PK
        string value
    }
    ACCOUNTS ||--o{ JOBS : receives
    ACCOUNTS ||--o{ RUNS : executes
```

## Delivery and trust chain

```mermaid
flowchart TB
    PR["Pull request"] --> CI["Python 3.14 quality gates"]
    PR --> Security["DevSecOps security gates"]
    CI --> Review["Protected main branch"]
    Security --> Review
    Review --> Tag["Semantic version tag"]
    Tag --> Build["Multi-architecture BuildKit build"]
    Build --> GHCR["GHCR image by digest"]
    Build --> SBOM["SPDX SBOM"]
    GHCR --> Sign["Keyless Cosign signature"]
    GHCR --> Attest["GitHub provenance attestation"]
```

## Design boundaries

- Gmail access is read-only; the service never needs a Gmail password.
- SQLite is intentionally single-host and offline-first, not a shared multi-node database.
- Scoring is deterministic and explainable; no email is sent to an LLM.
- Operations endpoints expose aggregate counts and must never expose email addresses or tokens.
- Monitoring is suitable for a single trusted deployment. Internet exposure requires TLS and authentication at a reverse proxy.
