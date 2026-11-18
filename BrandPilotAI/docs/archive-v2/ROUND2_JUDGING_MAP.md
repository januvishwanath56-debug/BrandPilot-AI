# Round 2: demonstration to judging-criterion map

From the Inkloom AI problem statement, the Round 2 scores total 100 points:

| Criterion | Weight | Show during judge demo |
|---|---:|---|
| Core workflow runs end to end | 30 | Create -> check -> source-backed findings -> revise -> human review -> approve/request changes |
| Technical depth and reliability | 25 | Rule engine with approved-source IDs, input limits, DB persistence, API tests, explicit AI fallback |
| Progress against the plan | 20 | Align delivered frontend/backend, data model and provenance with approved Round 1 proposal |
| Three named improvements | 15 | Show initial SourceTrace, IntentLock suggestions and ApprovalPulse events; commit to substantial Round 3 enhancements |
| Usability so far | 10 | Instant demo; guided sample; clear issues, actionable revisions and one-click persona switching |

## Live demonstration narrative
1. Show the LumaLeaf approved knowledge base (fictional data).
2. Load an unsupported marketing post into the editor and run the check.
3. Point to exactly which guideline or fact supports the finding.
4. Apply one recommended correction or edit manually, and re-check.
5. Send the revised content for review.
6. Switch to reviewer persona and approve it or request further changes.
7. Show persisted audit history, including revision number and reviewer note.

## Proof to capture
- Successful API tests and their output, with timestamp.
- A brief screen recording or screenshots for own evidence, even if not required for Round 2.
- Git commit history showing the building period.
- Live public URL that works in incognito.
- All limitations and services disclosed honestly.
