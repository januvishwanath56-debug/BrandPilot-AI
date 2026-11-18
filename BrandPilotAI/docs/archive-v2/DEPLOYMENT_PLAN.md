# Deployment plan (not yet deployed)

## Goal
Provide one public URL where the judge can open the app and test the full review, revision, and approval workflow without obtaining login credentials. The same URL should serve the compiled React frontend and `/api` routes, avoiding cross-site configuration mistakes.

## Planned method
- Build React with Vite in a Docker build stage.
- Serve FastAPI and the compiled SPA in a Python runtime container.
- Host that image as a web service that accepts a `PORT` environment variable and responds to `/api/health`.
- Use a managed PostgreSQL database via `DATABASE_URL` so sample drafts, approvals and audit history survive restarts. File-based SQLite is for development only. Some free hosting platforms have ephemeral disks.
- Set the API key only in the host's secret environment variables; never commit secrets or put them in `VITE_` browser-visible variables.

## Launch checklist
- [ ] Confirm database migrations/schema creation run and approved facts are seeded idempotently.
- [ ] Confirm HTTPS page loads in a fresh private window.
- [ ] Confirm no login, app-account, GitHub account or special invite required to see the demo.
- [ ] Confirm create-analyze-revise-review-approve cycle persists after page refresh.
- [ ] Confirm request changes and audit history views work.
- [ ] Confirm PDF/DOCX extraction, where supported, handles invalid content clearly.
- [ ] Confirm model failure gives transparent degraded mode and does not block basic checks.
- [ ] Confirm `README.md`, source URL and live app URL align with Round 2 form.

## Infrastructure risk
- Free web services may cold-start, shut down or lose files when restarted.
- Local SQLite is not suitable for persistent use on an ephemeral platform.
- Hosting provider signup or payment requirements may change; verify before deploying.
- If LLM service credentials are unavailable, demonstrate deterministic evidence checks and disclose the limitation rather than simulating LLM calls.
