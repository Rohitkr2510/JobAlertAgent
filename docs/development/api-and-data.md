# API and data reference

## Operations endpoints

| Endpoint | Success | Purpose |
|---|---|---|
| `GET /health/live` | `200` | Process is running and reports its version |
| `GET /health/ready` | `200` or `503` | Database, configuration, token key, and report storage are usable |
| `GET /metrics` | `200` | Prometheus text-format operational metrics |

Readiness returning `503` is expected during incomplete configuration and should remove the instance from traffic without restarting it.

## Metrics

| Metric | Type | Meaning |
|---|---|---|
| `jobalert_connected_accounts` | gauge | Configured Gmail accounts |
| `jobalert_enabled_accounts` | gauge | Accounts eligible for sync |
| `jobalert_jobs_collected` | gauge | Jobs stored locally |
| `jobalert_high_priority_jobs` | gauge | Current high-priority jobs |
| `jobalert_sync_failures_total` | gauge | Recorded failed synchronization runs |

Metrics deliberately avoid account email labels to prevent personal-data leakage and cardinality growth.

## Persistence

- `accounts` contains encrypted OAuth token material and account status.
- `jobs` contains normalized postings, scores, and application state.
- `runs` is the operational audit trail for synchronization attempts.
- `settings` stores scheduler and UI preferences.

Schema creation is idempotent. Future schema changes must use versioned migrations before backward-incompatible changes are introduced.
