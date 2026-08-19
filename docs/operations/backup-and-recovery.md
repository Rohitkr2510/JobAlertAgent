# Backup and disaster recovery

## Protected data

Back up `data/jobs.db`, `reports/`, and required configuration. Token backups are useful only with the corresponding encryption key; store the key separately from the encrypted token backup.

## Backup procedure

1. Stop synchronization or use SQLite's online backup mechanism.
2. Copy the database and reports to encrypted storage.
3. Record application version, schema version, timestamp, and checksum.
4. Test restoration periodically on an isolated host.

## Restore procedure

1. Stop JobAlertAgent.
2. Preserve the current files for investigation.
3. Restore configuration, database, reports, and—only if authorized—token material.
4. Confirm ownership and restrictive secret permissions.
5. Start the operations API and require readiness to pass.
6. Start the UI, run the offline self-check, then perform one controlled account sync.

## Objectives

- Initial recovery point objective: 24 hours.
- Initial recovery time objective: 4 hours for a single-host deployment.

These are engineering targets, not contractual guarantees. A release is not production-ready until a restore test has been recorded.
