# BrandPilot AI — Round 2 product plan

**Project owner:** Janu V — solo developer, The Oxford College of Engineering, Bengaluru.
**Competition:** CodeZen India 2026 / Inkloom AI brand-governance problem statement.
**Status:** Planning document only. No functional implementation is represented by this file.

## Goal
Deliver an independently usable, text-first pre-publication brand-governance workflow that accepts a draft, checks it against approved facts and guidelines, provides actionable source-linked findings, allows revision, and records a separate human approval decision.

## Scope promise
- A seeded fictitious brand, LumaLeaf, with explicit approved facts, prohibited/standard terms, and disclosure rules.
- Brand rule library (view, add, and edit rules as pilot allows).
- Content review interface with draft types: social post, advertisement, email, or document; support paste text first.
- Deterministic checks, with optional LLM-based suggestions behind an API key; transparent fallback and no fabricated evidence IDs.
- A result per problem: category, severity, excerpt, explanation, authoritative rule/fact reference, suggested correction.
- Revision loop with per-version content and per-version findings.
- Review queue, approval/request-changes decisions, immutable audit events.
- Demo access requiring no credentials; *not production authentication*.
- Working instructions, tests, and public deployment path.

## Explicit exclusions during Round 2
- Automated publication, bulk social network integrations, externally asserted legal compliance.
- Comprehensive image/logo understanding or claims of WCAG certification.
- Multi-tenant enterprise security and customer-data onboarding.
- A pretend AI experience that silently returns canned claims as though they were model-generated.

## Core model
Brand, Guideline, Submission, SubmissionVersion, Finding, AuditEvent.
Rules and facts include stable evidence IDs; a finding can cite only an existing guideline ID.

## Product states
Draft -> Reviewed -> Pending approval -> Approved OR Changes requested.
After creator edits, the draft returns to Draft and must be analyzed again before re-submission.
Approval on an unrevised high-risk finding is not automatically permitted; the demo can request changes instead.

## Solo developer priorities
1. Reliable local boot and seeded demo.
2. Rule-backed review and evidence links.
3. Browser-based revision and reviewer action.
4. Persistence and tests.
5. Deployment and documentation.
6. Optional LLM enhancements and document import after the above work.

## Submission integrity
The repository and submission should disclose significant AI-assisted code generation, external libraries and AI APIs, and any planning/templates prepared before the official 10:00 AM IST, 16 Nov 2026 build window. Functional implementation and development commits are to occur within the official window. Never represent demo personas as production-grade authentication.
