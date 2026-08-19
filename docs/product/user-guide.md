# User guide

## Supported workflow

1. Configure LinkedIn, Indeed, and Naukri to deliver alerts to Gmail.
2. Start JobAlertAgent and connect one or more Gmail accounts through OAuth.
3. Configure role, skill, location, experience, score, and recency filters.
4. Run a manual synchronization or enable the daily schedule.
5. Review prioritized jobs, update application status, and export Excel reports.

## Dashboard areas

| Area | Purpose |
|---|---|
| Overview | Counts, priorities, recent runs, and sync status |
| Email Accounts | Connect, disable, re-enable, or remove Gmail accounts |
| Jobs | Filter and inspect deduplicated opportunities |
| Applications | Track New, Saved, Applied, Interview, Offer, and Rejected states |
| Reports | Generate and download prioritized workbooks |
| Settings | Update deterministic filters and schedule |
| Logs | Review synchronization outcomes without token or message-body disclosure |

## Data interpretation

- **High Priority:** score meets `high_priority_score`.
- **Medium Priority:** score meets `minimum_score`.
- **Needs Review:** incomplete or ambiguous source data requires manual review.
- **Date verified:** the posting time was extracted; otherwise email receipt time is used.
- **New:** the job URL or derived identity has not been stored before.

## Known limitations

- Job-board email HTML can change and require parser maintenance.
- Email receipt time is not always the posting time.
- SQLite supports one primary deployment, not concurrent clustered writers.
- Gmail synchronization requires internet access; parsing and reporting do not.
