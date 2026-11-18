# Privacy and private pilot operation

## Public demo

Default `AUTH_MODE=demo`. Personas are selectable; session UUIDs in browser localStorage partition ordinary queries but are not authenticated tenant boundaries. Never use confidential company material here. Uploaded raw files are parsed in memory, not retained. Extracted text, sources, findings and audit records persist in the configured database. No browser analytics were added by the application.

## Optional private pilot

Deploy separately from the public judge demo. Set `AUTH_MODE=private`, a cryptographically random `AUTH_SECRET` of at least 32 characters and `AUTH_USERS_JSON` containing username -> role/password_hash objects. Run `python provision_user.py` from backend to generate each account record interactively; combine the records into one JSON object in your host's secret settings. Passwords are entered with getpass and hashed with salted PBKDF2-SHA256 (600,000 rounds). Never commit the resulting account configuration.

Roles: creator writes and views own drafts; reviewer views workspace submissions and makes decisions; manager maintains custom sources and can review. Identity and role are resolved from the server account configuration, ignoring demo headers. Tokens last 8 hours and are stored only in frontend memory; reload signs out. Sign-out discards the local token; it is not server-side revocation. Rotate AUTH_SECRET to invalidate all sessions. Removing an account revokes access. Self-approval is rejected even if the creator's role is later changed.

Login attempts are capped per username in a process-local 15-minute window. AI calls are capped by session and day in process memory. These reset on restart and are not distributed controls. Put a managed identity service, proxy rate limiting, monitoring, backup/recovery and concurrency tests in place before sensitive production use. There is no registration, password reset or SSO flow.

## External AI

AI starts off and every scan requires the enabled toggle to use the provider. When enabled, submitted text and up to 60 active source records are sent to OpenRouter and its selected model provider. The app cannot guarantee their retention/training policies; consult https://openrouter.ai/privacy . Keep public-demo data fictional. The server key never enters browser responses. Responses must use existing source IDs and excerpts; validation does not establish semantic truth. Human review remains mandatory.

## Retention / deletion

The demo has no automatic retention purge. The deployment owner can remove session data using a database transaction after exporting any needed evidence: delete findings, analysis_runs, audit_events and submission_versions belonging to matching submissions, then submissions, policy_events and custom guidelines for that session. Always scope the transaction to the intended session and back up first. There is no user-facing permanent-delete control, and audit records cannot be removed via the application API.
