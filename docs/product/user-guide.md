# User guide

## Supported workflow

1. Configure LinkedIn, Indeed, and Naukri to deliver alerts to Gmail.
2. Start JobAlertAgent and connect one or more Gmail accounts through OAuth.
3. Configure role, skill, location, experience, score, and recency filters.
4. Run a manual synchronization or enable the daily schedule.
5. Review prioritized jobs in the Jobs table.
6. Move relevant jobs through the application pipeline: `New → Saved → Applied → Interview → Offer` or `Rejected`.
7. Record follow-up dates, next actions, and notes for applications.
8. Use the Applications workspace each day to review applications and follow-ups due.
9. Export Excel reports when a broader offline view is needed.

## Dashboard areas

| Area | Purpose |
|---|---|
| Overview | Counts, priorities, recent runs, and sync status |
| Email Accounts | Connect, disable, re-enable, or remove Gmail accounts |
| Jobs | Search, filter, sort, paginate, inspect, and update deduplicated opportunities |
| Applications | Daily application workspace, pipeline counts, applications made today, and follow-ups due |
| Reports | Generate and download prioritized workbooks |
| Settings | Update deterministic filters and schedule |
| Logs | Review synchronization outcomes without token or message-body disclosure |

## Jobs table

Every job has a permanent **Job ID** (`unique_id`). This identifier is the row identity used for application updates, so changing one row's status does not depend on its position in the table.

The Jobs table supports:

- Search across Job ID, title, company, location, skills, source, and other visible job data.
- Filtering by Gmail account, source, application status, priority, location, experience, score, and received-date range.
- Sorting by newest, score, company, title, or status.
- Pagination with configurable page size.
- Inline editing of **Application Status only**. Job metadata remains read-only.
- A dedicated tracking editor for **Follow-up Date**, **Next Action**, and **Notes**.
- A job URL for opening the original posting.

Changing a status updates only the selected job's `unique_id`. When a job is first changed to `Applied`, the application timestamp is recorded automatically if one does not already exist.

## Application pipeline

| Status | Meaning |
|---|---|
| New | Newly collected job that has not yet been reviewed or saved |
| Saved | Job selected for possible application |
| Applied | Application has been submitted |
| Interview | Interview process is active |
| Offer | Offer received |
| Rejected | Application or opportunity is no longer active |

## Daily application workflow

Use the **Applications** tab as the daily work queue:

1. Start with `New` and `Saved` jobs.
2. Apply to the relevant opportunities.
3. Change the status to `Applied`; the first application timestamp is captured automatically.
4. Add a follow-up date when an employer or recruiter needs a response.
5. Add a clear next action, such as `Follow up with recruiter`, `Prepare Kubernetes round`, or `Send referral request`.
6. Keep important context in Notes.
7. Review **Follow-ups due** every day before starting new applications.
8. Use the pipeline counts to track progress from discovery to interview and offer.

## Tracking fields

- **Applied Date:** timestamp recorded when a job first moves to `Applied`.
- **Follow-up Date:** optional date for the next recruiter/employer follow-up.
- **Next Action:** the concrete next step for the application.
- **Notes:** free-form application context.
- **Job ID:** stable unique identifier for the job record.

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
