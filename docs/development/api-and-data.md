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
- `jobs` contains normalized postings, scores, and application tracking state.
- `runs` is the operational audit trail for synchronization attempts.
- `settings` stores scheduler and UI preferences.

### `jobs` application-tracking fields

| Field | Purpose |
|---|---|
| `unique_id` | Stable primary key and row identity for a job |
| `application_status` | Current application state: `New`, `Saved`, `Applied`, `Interview`, `Offer`, or `Rejected` |
| `applied_at` | Timestamp captured when the job first moves to `Applied` |
| `follow_up_date` | Optional date for the next follow-up |
| `next_action` | Optional concrete next step |
| `notes` | Optional application notes and context |

Status updates use `unique_id`, not a table row number or display position. This keeps updates tied to the correct job when filters, sorting, or pagination change the visible order.

Schema creation is idempotent. Existing databases are upgraded by adding missing application-tracking columns without replacing existing job records. Future schema changes must use versioned migrations before backward-incompatible changes are introduced.
