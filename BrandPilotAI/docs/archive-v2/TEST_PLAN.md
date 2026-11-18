# Acceptance test plan — BrandPilot AI v1

The following tests are **planned**, not recorded outcomes. Collect actual results during implementation.

## Scenario A — evidence conflict
Approved source F-001 states the LumaLeaf reusable bottle contains 60% post-consumer recycled plastic. Submit: "Our LumaLeaf bottle is 100% plastic-free."
Expected: issue explaining the contradiction, source F-001, correction reflecting 60% recycled plastic, status not marked approved.

## Scenario B — unverified marketing superlative
Submit: "The best bottle in the world, guaranteed to save the planet."
Expected: unsupported promotional claims marked `needs_evidence`, not automatically declared false.

## Scenario C — approved content
Submit: "Meet LumaLeaf: a reusable bottle made with 60% post-consumer recycled plastic."
Expected: zero critical issues, with a clear description of what was and was not checked.

## Scenario D — revision and human review
Create draft -> analyze -> revise to a compliant version -> analyze again -> send for approval -> switch to reviewer demo -> approve -> reload.
Expected: status and version history persist, the approving actor is distinct from creator, and audit actions are visible.

## Scenario E — cannot approve stale analysis
Analyze a draft -> change its content -> attempt to submit old findings for approval.
Expected: reject until newly revised version is re-analyzed.

## Scenario F — visibility and error handling
Open public demo link in private browser; submit too-long content and invalid unsupported file type.
Expected: useful errors and no silent failures.

## Scenario G — AI outage
Remove API key or simulate model failure.
Expected: deterministic checks still work; UI truthfully shows which analysis mode ran.

## Scenario H — audit and revisions
Request changes with comment; revise; approve; inspect history.
Expected: all major transitions visible with timestamps and content version references.
