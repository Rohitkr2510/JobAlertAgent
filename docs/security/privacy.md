# Privacy and data lifecycle

## Data minimization

JobAlertAgent requests Gmail read-only access and queries only configured sender domains and time windows. It stores normalized job information and a bounded context excerpt, not an archival copy of the mailbox.

## Data classification

| Data | Classification | Storage |
|---|---|---|
| OAuth client and refresh token | Secret | Mounted `secrets/`, token encrypted at rest |
| Token encryption key | Secret | Mounted `secrets/token.key` |
| Account email | Personal | SQLite `accounts`, application logs use a hash |
| Job alert content | Personal/internal | SQLite and generated reports |
| Aggregate metrics | Operational | Prometheus |

## Retention and deletion

- Operators define retention according to their job-search needs.
- Removing an account deletes its stored encrypted token record.
- Full erasure requires deleting the SQLite database, reports, backups, and token material.
- Logs must be retained for the shortest operationally useful period.
- Backups inherit the highest classification of their contents.

## Logging rules

Never log OAuth tokens, authorization responses, message bodies, full account addresses, encryption keys, or report contents. Use the existing hashed account identifier for correlation.
