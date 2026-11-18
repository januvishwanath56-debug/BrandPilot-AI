# BrandPilot AI - Proof before publish

An evidence-led brand review workspace for CodeZen India 2026 Round 2. Built from the supplied Version 2 project, preserving React/JSX, FastAPI, SQLAlchemy and optional OpenRouter integration.

**Owner:** Janu V, solo participant, The Oxford College of Engineering, Bengaluru.

## Run locally

Install Python 3.12 and Node 22.12+; from this repository:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
cd frontend
npm ci
npm run build
cd ..
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. `start-local.ps1` performs the same setup. SQLite persists locally; deployment must use external PostgreSQL. Optional settings belong in `backend/.env` copied from `.env.example`, never in frontend files.

## Judge walkthrough (no account or key needed)

1. Click **One-click demo**. The fictional LumaLeaf campaign contains four known issues.
2. Inspect the plastic-free claim: FACT-01 supplies the exact approved 60% recycled-plastic fact. Other unsupported claims say **needs evidence**, not false.
3. Insert a correction; the old report becomes unavailable until inspection. Edit the remaining claims and inspect again, saving revision 2.
4. Click **Request approval**, then switch to **Reviewer**. Request changes with a reason or record approval. High-risk approval requires a checked override and written justification.
5. Open **Decision trail** to see revision history, inspection snapshots, source evidence, comments and the final human decision. Export approved copy or a JSON review report.
6. Switch to **Manager**, open **Brand library**, add an exact-phrase rule, and inspect new copy containing that phrase. Policy changes block approval of stale reviews.

Approved example:
> Meet LumaLeaf: a reusable 750 mL bottle made with 60% post-consumer recycled plastic. Includes a 12-month limited manufacturing warranty. Explore our collection today.

## Implemented

- Text, selectable PDF, DOCX (including tables) and TXT import; 5 MB upload, 30 PDF pages and 10,000-character review limits. Oversized expanded DOCX archives are rejected.
- Source-backed rule findings, exact excerpts, severity, explanation, proposed correction, evidence-needed labels and source snapshot identifiers.
- Optional OpenRouter advisory, explicitly switched off initially. Only `openrouter/free` or IDs ending in `:free` are accepted. Malformed responses, unavailable providers and quota limits fall back to labelled local rules.
- Content revisions, repeated inspection snapshots, human approvals/change requests, comments, audit events, source-change history API and stale-policy approval prevention.
- Searchable fact/rule library, current-revision recurring-rule counts, evidence-gap counts and approved-copy export.
- Public demo persona mode; optional private single-organisation login with PBKDF2 password hashes, signed expiring bearer tokens, server-side roles, creator ownership filtering and self-approval prevention.
- Responsive editorial UI, keyboard focus styling, labelled navigation, skip link and modal keyboard containment.

## Verification on 18 November 2026

- **24 backend tests passed** in Python 3.12; one upstream Starlette/httpx deprecation warning.
- **Vite production build passed**, including on this Windows workspace using the native config loader.
- **Real browser workflow verified:** demo findings -> correction -> revision 2 -> fresh inspection -> review request -> reviewer approval -> audit trail -> approval persists after reload.
- **390px mobile check:** no horizontal overflow; mobile navigation works. Desktop audit layout visually inspected.
- PDF, DOCX and TXT extraction tested through API integration tests.
- Private identity/role boundaries tested through API integration tests; private-login browser flow not independently exercised.
- Live OpenRouter inference **not run: no configured key**. Provider behaviors tested offline with mocked responses.
- Public hosting, Neon connectivity, Docker image execution and incognito public links **not yet verified**.

Run backend tests from `backend`: `..\.venv\Scripts\python.exe -m pytest -q`. Run frontend build from `frontend`: `npm run build`.

## Deploy

Follow [DEPLOY.md](docs/DEPLOY.md). Two supported configurations:

- Render Docker service + Neon PostgreSQL: one URL for UI and API.
- Vercel frontend (`frontend` root) + Render API + Neon: set `VITE_API_BASE_URL` in Vercel and exact `ALLOWED_ORIGINS` on Render.

The project has not been pushed or published by this assistant. Add the real working and repository links to [SUBMISSION.md](docs/SUBMISSION.md), then test them without signing in.

## Boundaries

This is a tested hackathon MVP and single-organisation pilot, **not a certified production security/compliance product**. Demo session IDs are browser-scoped conveniences, not authentication. Use fictional data on the public demo. Private mode is separate and requires account provisioning; it is not SSO or enterprise tenancy.

The rule engine recognizes configured phrases, not every semantic claim. AI source-ID checks do not prove that a model's interpretation is correct. No OCR, image/logo recognition, vector retrieval, external publishing, password reset, distributed rate limiting or full WCAG audit is claimed. Small single-instance deployment is the intended scale. The initial seed corpus is read-only; managers can add/edit custom sources.

See [SECURITY.md](docs/SECURITY.md), [AUDIT.md](docs/AUDIT.md), [TEST_RESULTS.md](docs/TEST_RESULTS.md) and [SUBMISSION.md](docs/SUBMISSION.md). Older V2 documents remain in `docs/archive-v2` as unverified historical context.

## Disclosure

Version 2 supplied by Janu is the starting point. ChatGPT/Codex materially assisted the new audit, implementation, tests and documentation. These are AI-assisted components; no human user study, model-accuracy benchmark, public deployment or unsupported build-history claim is made. Do not backdate Git history. Janu should review and understand the code before submitting and report personal contributions truthfully.

Dependencies: React, Vite, Lucide, FastAPI, Uvicorn, SQLAlchemy, Pydantic, httpx, python-dotenv, python-multipart, psycopg, PyMuPDF and python-docx. `requirements-lock.txt` and `frontend/package-lock.json` record installed versions. Respect each dependency's licence (including PyMuPDF's AGPL/commercial licensing); do not infer a blanket licence for third-party packages from this repository.
