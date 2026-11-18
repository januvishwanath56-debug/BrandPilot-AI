# CodeZen India 2026 - Round 2 submission

Team: BrandPilot AI. Participant: Janu V (solo), The Oxford College of Engineering, Bengaluru.
Deadline supplied by organiser: 19 November 2026, 10:00 AM IST.

## Links to complete after publishing

- Working project: **INSERT VERIFIED PUBLIC URL**
- Source repository: **INSERT PUBLIC GITHUB URL**
- Updated PDF: **UPLOAD BrandPilot_AI_Round2_Janu_V.pdf AND INSERT PUBLIC VIEWER LINK**

## Completed features

Approved-source library, paste/PDF/DOCX/TXT intake, deterministic brand/claim/tone/accessibility phrase checks, source-backed explanations and corrections, optional validated OpenRouter advisory with fallback, editable content revisions, human approvals/change requests and overrides, comments, inspection/source snapshots, audit history, private pilot accounts/roles, no-sign-in judge sandbox, recurring-issue counts, approved-text and JSON exports, responsive interface and deployment configuration.

## Technology and implementation

React 19 / JSX, Vite 7, FastAPI, SQLAlchemy, Pydantic, SQLite locally / PostgreSQL deployment adapter, PyMuPDF and python-docx extraction, httpx OpenRouter adapter. Exact installed versions are in lockfiles. Source-set digests prevent approval against changed policies; each inspection retains its evidence. Password hashes and signed expiring tokens support an optional single-organisation private pilot. UI and API can share a Render Docker service, or Vercel can host the frontend with a Render/Neon backend.

## Changes from Round 1

Preserved the text-first evidence/revision/human-approval workflow. Deferred pgvector, semantic retrieval and image recognition. Reused the Version 2 fictional reusable-bottle corpus, rather than expanding the proposed personal-care example. Added no-account sandbox personas for independent judging and separate optional private identity. Added basic current-revision insights earlier than planned. No production-security certification or model-accuracy claim.

## Three substantial Round 3 improvements

1. **SourceTrace+:** retrieve pinpoint passages from larger approved brand documents with version/expiry support; evaluate on at least 50 labelled supported/contradicted/unknown claims, report citation validity and abstention accuracy.
2. **IntentLock:** produce constrained alternative rewrites with sentence-level diffs and creator intent notes; benchmark factual preservation and usefulness with real reviewers. Current suggestions alone do not fulfill this planned evaluation.
3. **ApprovalPulse+:** managed identity, assigned-reviewer queues, revocation/notifications and time-based repeated-issue analysis; add concurrent-update and multi-user integration tests. Current audit records and simple counts are the starting point.

## Verification and limitations

24 offline backend tests passed; production frontend build passed; localhost browser revision/approval/persistence workflow and 390px responsive check completed. Live OpenRouter and public hosting remain unverified until credentials and deployment are supplied. No OCR, image/logo detection, enterprise SSO or semantic benchmark is claimed.

## Contribution / tools disclosure

Janu V is the solo participant and project owner. ChatGPT/Codex supplied significant code generation, audit, debugging, test and documentation assistance. Version 2 was supplied as the starting codebase. Report Janu's actual personal review, learning, deployment and testing work accurately; do not attribute unperformed manual work or fabricated commit dates to anyone. No interviews or user study results were collected during this session.
