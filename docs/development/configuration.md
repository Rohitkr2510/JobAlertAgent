# Configuration reference

The default filter file is `config/job-filters.yaml`.

| Field | Type | Meaning |
|---|---|---|
| `hours` | integer | Gmail and job recency window |
| `minimum_score` | integer | Minimum score for a recommended job |
| `high_priority_score` | integer | High-priority threshold |
| `maximum_experience_years` | integer | Maximum preferred experience requirement |
| `preferred_locations` | list | Location matches that increase score |
| `role_keywords` | list | Accepted role-family terms |
| `skill_keywords` | list | Skills used for scoring and explanation |
| `sender_domains` | list | Gmail sender-domain allowlist |

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `JOBALERT_ROOT` | `.` | Application data root |
| `JOBALERT_DATABASE` | `data/jobs.db` | SQLite path relative to the root |
| `JOBALERT_CONFIG` | `config/job-filters.yaml` | Filter configuration path |
| `JOBALERT_TOKEN_KEY` | `secrets/token.key` | Token encryption key path |
| `JOBALERT_TIMEZONE` | `Asia/Kolkata` | Scheduler timezone |
| `GRAFANA_ADMIN_PASSWORD` | development value | Grafana administrator password |

Secrets must be supplied through mounted files or an external secret manager, never committed environment files.
