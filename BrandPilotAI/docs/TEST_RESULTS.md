# Recorded verification - 18 November 2026 (IST)

## Automated

`python -m pytest -q` from backend: **24 passed**, 18.46 seconds at the expanded-suite run. One upstream Starlette TestClient/httpx deprecation warning. Tests use isolated in-memory SQLite databases and mocked provider responses; they are not production load tests.

Original 16 tests: seeded sources, contradictions, needs-evidence labels, approval permissions, explicit overrides, stale revisions, session scoping, custom rules, TXT/PDF/DOCX extraction, AI key absence, opt-out, source validation and quota fallbacks.

Added 8 tests: stale-policy approval rejection, retained inspection runs, whitespace/null rejection, comments/policy audit, default AI opt-out, malformed provider envelopes, non-free model guard and private identity/ownership/role boundaries.

`npm run build -- --configLoader native`: **passed**, 1,579 modules, about 273 kB JS / 84 kB gzip. Native config loading avoids an esbuild parent-directory sandbox restriction on this Windows host; it is now the default build script.

## Browser observations

Real in-app Chromium UI, localhost, with no live AI key:

1. One-click sample produced four findings including plastic-free -> FACT-01.
2. Applying a suggestion changed the editor and invalidated the visible report.
3. Editing to approved facts and inspecting saved revision 2 with zero known issues.
4. Requesting review locked editing; Reviewer recorded a comment and approval.
5. Decision trail showed creation, two inspections, revision, review request and approval, with both content versions and inspection archives.
6. Reload preserved the approved record and approved count.
7. 390 x 844 viewport: document width 375, viewport width 390; no horizontal overflow. Mobile menu opened; desktop timeline visually inspected.

Screenshot evidence: `../BrandPilot-verified-approval.png` in the enclosing outputs folder. Browser tooling emitted its own Statsig initialization warnings; no claim of a clean application-console audit is made.

## Explicitly unverified

Live OpenRouter request (no configured key), Docker execution, hosted PostgreSQL, public URL/incognito accessibility, private-login UI, comprehensive accessibility, concurrency/load, OCR/image analysis and model-accuracy benchmarks. No external user testing or fabricated user feedback is claimed.
