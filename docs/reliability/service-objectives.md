# Service objectives

## Indicators and objectives

| Capability | Indicator | Initial objective |
|---|---|---|
| Operations availability | Successful liveness requests | 99% per 30 days while host is scheduled to run |
| Readiness | Successful readiness requests | 99% per 30 days excluding planned configuration |
| Scheduled sync | Successful enabled-account runs | 95% per 7 days |
| Data freshness | Completed sync within configured window | 95% of scheduled runs |
| Report integrity | Successful report creation after sync | 99% per 30 days |

## Alerting principles

- Alert on user-visible symptoms and sustained failure, not single transient events.
- Every actionable alert must link to the operations runbook.
- Personal data must not appear in labels or notification text.
- Warning alerts create work; critical alerts require immediate operator attention.

## Capacity assumptions

The initial design targets a small number of Gmail accounts and personal job-alert volume on one host. Before materially increasing load, measure database size, sync duration, Gmail quota consumption, report generation time, and metrics cardinality.
