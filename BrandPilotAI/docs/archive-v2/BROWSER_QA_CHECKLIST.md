# BrandPilot AI V2 — browser and deployment quality checklist

Use this **after** `npm install` and `npm run dev` on Windows and again on Render in an incognito window.

- [ ] Desktop at 1440px: heading, two-column desk, cards and reviewer controls are readable with no horizontal overflow.
- [ ] Mobile at 390px: menu opens/closes, typography wraps, cards stack and buttons are tappable.
- [ ] No errors in the browser developer-console during page load.
- [ ] One-click demo creates a new backend draft and shows highlighted risky claims.
- [ ] The `100% plastic-free` finding cites stored approved fact `FACT-01`; not just a generic LLM statement.
- [ ] Apply a suggested correction → editor changes, old findings hidden until a new scan.
- [ ] Re-inspect the edited copy → revision increments; previous findings do not remain as current.
- [ ] Missing OpenRouter key → app says rules-only, and deterministic findings still work.
- [ ] With optional key, AI-enabled scan correctly displays `rules + OpenRouter` only if the model returned usable output; no fake success labels.
- [ ] An AI rate-limit or outage returns `rules only` with saved deterministic findings.
- [ ] Submit for human approval; the Creator cannot approve their own content without switching demo personas.
- [ ] Reviewer change-request requires a comment; high-risk override requires checkbox + meaningful justification.
- [ ] Successful approval appears in Decision trail with actor, time and revision.
- [ ] Refresh the page; previously saved drafts and review events persist (with external PostgreSQL in deployment).
- [ ] Add custom phrase rule → it triggers; disable it → it stops triggering.
- [ ] Import a TXT, selectable-text PDF and DOCX; invalid file types return a clear error.
- [ ] Export JSON report to a local file.
- [ ] Public deployment opens in **incognito without sign-in**.
- [ ] `api/health` works on the deployed HTTPS site.
- [ ] No `OPENROUTER_API_KEY`, `DATABASE_URL` with credentials, `.env` file or other secret is committed to GitHub.
- [ ] Submission links: GitHub repository, working web URL and updated PDF all open for a stranger.
