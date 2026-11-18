# Audit and implemented fixes - 18 November 2026

The original V2 source already implemented the deterministic review, revision and approval loop. It was not rebuilt from scratch.

| Finding | Change |
|---|---|
| Docker referenced missing backend requirements | Restored manifest; reproducible root lockfile; Docker installs lockfile and uses npm ci |
| README setup paths did not match supplied files | Replaced setup with tested root commands and helper script |
| Selectable role headers were the only identity mechanism | Retained explicit sandbox; added optional private signed-token identity and server role resolution |
| Source edits could leave an analyzed draft eligible for approval | Stored source-set digest; reject stale source sets at review request and approval |
| Reanalysis overwrote inspection evidence | Added immutable AnalysisRun snapshots including all active sources and findings |
| Source changes had no record | Added PolicyEvent snapshots and policy-history endpoint |
| AI enabled automatically; API default also enabled it | Both default off; explicit user opt-in |
| Invalid JSON shape could be marked completed or crash | Validate envelope, choices, message and findings; label rejected response |
| Long drafts silently sent only first 6,000 characters to AI | Send supported 10,000-character content limit |
| Paid model IDs could be configured inadvertently | Reject IDs outside free router / :free variants |
| Whitespace-only input and explicit nulls bypassed intent | Strip/validate inputs; reject null required policy fields |
| DOCX expansion unconstrained | Bound expanded archive size and file count before parsing |
| All-caps excerpt contained an invented ellipsis | Return an exact substring |
| Generic guidance inserted as literal marketing copy | Guidance-only findings no longer expose insertion button |
| Metadata edits silently forked a campaign | Freeze title/channel for saved records; new samples create new campaigns |
| Timestamps lacked timezone after SQLite reload | Serialize naive stored UTC values with explicit UTC offset |
| CORS fixed to localhost | Configurable exact allowed frontend origins |
| Missing collaboration and insight surface | Comments, approved-copy export, inspection archive, evidence-gap and repeat-rule counts |

## Remaining limits

No independent security audit, production tenancy, schema migration framework, pagination, OCR, visual identity model, distributed abuse prevention or measured semantic accuracy. PostgreSQL row locking serializes submission mutations; SQLite development mode is not the concurrency target. Policy changes occurring concurrently with approval are not serialized across all source rows; single-instance sequential use is tested. The pilot requires additional concurrency and operational hardening before sensitive production use.
