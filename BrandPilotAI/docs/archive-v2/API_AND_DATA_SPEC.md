# BrandPilot AI — implementation blueprint (planning-only)

## Domain objects
| Entity | Primary purpose | Key fields |
|---|---|---|
| Brand | Identifies the demo organisation | id, name, slug |
| Guideline | Approved fact or editorial policy | id, brand_id, code, category, text, optional trigger, expected correction, active |
| Submission | Draft lifecycle | id, creator, title, channel, state, revision, last_analyzed_revision |
| SubmissionVersion | Immutable content snapshots | submission_id, revision, text, actor, created_at |
| Finding | Issues for one exact version | submission_id, revision, rule_code, severity, excerpt, reason, evidence_status, suggestion |
| AuditEvent | Review trail | submission_id, revision, actor, role, action, note, timestamp |

## Planned REST routes
`GET /api/health` — health check.
`GET /api/config` — name/AI-enabled indicators and supported formats.
`GET /api/brands` — available demo brand.
`GET /api/guidelines` — current source records.
`POST /api/guidelines` — add supported demo policy.
`PATCH /api/guidelines/{guideline_id}` — update an existing policy; audit the policy change.
`GET /api/submissions` — optionally filter by status.
`POST /api/submissions` — create creator draft.
`GET /api/submissions/{id}` — fetch content, findings, and current state.
`PATCH /api/submissions/{id}` — create a new immutable content revision.
`POST /api/submissions/{id}/analyze` — run deterministic / optional model review and link sources.
`POST /api/submissions/{id}/request-review` — send analyzed revision for human review.
`POST /api/submissions/{id}/decision` — reviewer approves or requests changes.
`GET /api/submissions/{id}/history` — review state transitions and revisions.
`GET /api/stats` — counts by workflow state and findings.
`POST /api/extract` — safe text extraction from a supported text document.

## State machine
- `draft` -> `reviewed` after current revision is analyzed.
- `reviewed` -> `pending_review` after creator requests human review.
- `pending_review` -> `approved` by designated demo reviewer, with recorded justification for unresolved high severity findings.
- `pending_review` -> `changes_requested` by designated demo reviewer, with a comment.
- `draft`, `reviewed`, or `changes_requested` -> new `draft` revision on content edit.
- `approved` is immutable in v1; a new submission would be needed to continue.
- Re-review cannot rely on findings from a previous revision.

## SourceTrace MVP constraints
- A finding must reference an existing policy code or explicitly say no approved support is available.
- Distinguish `contradicted`, `needs_evidence`, `stylistic_rule`, and `supported`.
- An absent approved source is *not* proof that the claim is false.
- Detect some high-risk patterns even without an external AI key.
- LLM failure must be distinguishable from a successful full analysis.

## Trust boundaries
- Do not expose API keys to browser code.
- Only send fictitious demo material to external AI by default.
- Limit size of uploads; validate extensions and parsing errors.
- Do not claim demo-role headers are secure identity verification.
- Do not let a language model choose permissions or bypass approval checks.
- Server-side reviewer approval always creates a durable audit event.
