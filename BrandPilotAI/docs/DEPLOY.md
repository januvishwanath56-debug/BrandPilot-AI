# Deploy BrandPilot AI

## Option A: one Render URL (least setup)

1. Push this folder's contents to your public GitHub repository. Keep existing repository history if you have one; do not copy .env, databases, virtual environments or node_modules. Inspect `git status` before committing.
2. Create a Neon PostgreSQL database. Copy its pooled connection string with `sslmode=require` into Render's secret `DATABASE_URL` setting, never into source code.
3. Create a Render Web Service from the repository. Runtime **Docker**, repository root, free instance if eligible, health path `/api/health`.
4. Set `AUTH_MODE=demo` for the public judge link. Optionally set `OPENROUTER_API_KEY`, `OPENROUTER_MODEL=openrouter/free`, `AI_DEMO_DAILY_LIMIT=35`, `AI_DEMO_SESSION_LIMIT=4`.
5. Deploy and open `/api/health`, then the homepage. The startup creates missing tables and fictional source records. Existing V2 databases get the new history tables; existing drafts must be analyzed again to create their policy snapshots.
6. Run the README walkthrough in an incognito browser. Record the actual URL in SUBMISSION.md.

Do not use SQLite on an ephemeral hosting filesystem. Render free web services currently sleep after 15 minutes without incoming traffic, so allow time for cold start before judging. See https://render.com/docs/free . No uptime guarantee is implied.

## Option B: Vercel frontend + Render backend

1. Deploy the backend with Option A first. It can continue serving the UI too.
2. Import the same GitHub repository into Vercel. **Root directory: frontend**. Framework: Vite. Build: `npm run build`. Output: `dist`.
3. Add `VITE_API_BASE_URL=https://YOUR-SERVICE.onrender.com` to Vercel, then deploy/redeploy. This variable is public and contains only the API origin.
4. On Render set `ALLOWED_ORIGINS=https://YOUR-PROJECT.vercel.app` using the exact production origin, no trailing slash. For multiple origins, use commas. Redeploy/restart Render.
5. Open the Vercel URL in incognito and complete the full workflow. If requests fail, check that the API is awake, the URL uses HTTPS, the environment variable existed at frontend build time and the exact frontend origin is allowed.

Do not paste the OpenRouter key or database URL into any `VITE_` setting. This delivery deliberately uses a separate long-running API; a Vercel-only FastAPI conversion is not claimed or tested.

## Before submission

- Public website loads without an account in demo mode.
- Public GitHub source link opens without an account.
- Uploaded updated PDF has public viewer access.
- Real live AI only claimed if a successful opted-in review actually ran.
- Walk through review, revision, approval and reload from the public URL.

Official references checked 18 Nov 2026: https://render.com/docs/free ; https://vercel.com/docs/frameworks/backend/fastapi ; https://openrouter.ai/openrouter/free ; https://openrouter.ai/privacy . Free-model availability and host plans can change.
