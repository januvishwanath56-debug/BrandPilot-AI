# Deploy BrandPilot AI on Render + Neon — zero-cost target

This guide is for a **public demonstration** during CodeZen India Round 2. It is not a production-security setup.

## 1. Verify locally (do this before deployment)

- Backend: `http://127.0.0.1:8000/api/health` returns `{"status":"ok",...}`.
- Frontend: `npm run dev` opens a polished desk at `http://localhost:5173`.
- Browser workflow: Inspect risky sample → view source evidence → edit → reinspect → request approval → switch Reviewer → approve or request changes → inspect Decision trail.
- Production frontend compilation: run `npm run build` inside `frontend` and verify that `frontend/dist/` appears. This directory is generated, **not** committed.
- Backend: run `python -m pytest -q` inside `backend`.

## 2. Make the GitHub repository public

In your existing local repository root:

```bat
git status
git add .
git commit -m "feat: upgrade publishing desk and integrate OpenRouter free AI"
git push origin main
```

Do **not** push `backend/.env` or your API key. `.gitignore` excludes `.env`; always verify `git status` anyway.

## 3. Create persistent free PostgreSQL on Neon

1. Register at https://console.neon.tech/ with your chosen account.
2. Create a new project called `brandpilot-demo` (select a region near the Render service).
3. In its dashboard copy the **Postgres connection string** (`postgresql://...`). Store it privately. Do not post the database URL in a chat or screenshot; it contains a password.
4. Keep the project's free-tier usage within its current published limits. PostgreSQL tables seed automatically during application startup.

Why Neon? Render free web service files disappear after restart or sleep. SQLite is safe for **local** development but not for the deployed demo.

## 4. Create the Render web service

1. Open https://dashboard.render.com/ → **New → Web Service**.
2. Select your public GitHub repository. Choose **Docker** as the runtime. The Dockerfile in the project root compiles Vite and serves the compiled frontend through FastAPI on a single port.
3. Name: `brandpilot-ai-demo` (or another available name).
4. Instance: **Free**.
5. Add environment variables under **Environment**:

| Variable | Value | Required? |
|---|---|---|
| `DATABASE_URL` | Neon connection string | **Yes** for persistence |
| `OPENROUTER_API_KEY` | Private key from https://openrouter.ai/settings/keys | No, rules work without it |
| `OPENROUTER_MODEL` | `openrouter/free` | No, default is already set |
| `AI_DEMO_DAILY_LIMIT` | `35` | No, default is 35 |
| `AI_DEMO_SESSION_LIMIT` | `4` | No, default is 4 |

Do **not** set a `VITE_OPENROUTER_API_KEY`—that would put the secret into public JavaScript.

6. Select **Deploy Web Service**. Wait for `Live`. Monitor the Render logs if it fails. If Render offers a Blueprint flow, `render.yaml` is also included, but the manual dashboard process is more explicit.
7. Visit `https://YOUR-SERVICE.onrender.com/api/health` then `https://YOUR-SERVICE.onrender.com/`.

## 5. Check the deployment in an incognito window

- Public URL shows the actual application (not a sign-in page or Swagger only).
- Click **One-click demo** → an approved LumaLeaf source is shown with a finding.
- Revise and re-inspect; old findings must not persist as current findings.
- Click **Request approval**; choose **Reviewer** and make a decision with a comment.
- Reload the page and return to Decision trail to prove PostgreSQL persistence.
- Test clean content and one file import.
- If OpenRouter is configured: run one short AI-enabled review, confirm its engine status, then turn the AI toggle **off** for repeated demos to conserve the 50-request daily allowance. A successful HTTP call does not guarantee additional AI findings.
- Inspect the browser console and mobile layout. Test all links from a second device if possible.
- On a sleeping free web service, the first request may take approximately a minute. Open the website shortly before live judging and check it again.

## 6. Troubleshooting

- **500 after launch:** Ensure `DATABASE_URL` is the correct complete Neon connection string and that Render is allowed to connect.
- **No database persistence:** Ensure `DATABASE_URL` is not SQLite. Render's free local filesystem is ephemeral.
- **Failed Docker build:** Confirm Vite can compile locally (`npm install && npm run build`), and that the build uses the root Dockerfile.
- **AI status `not_configured`:** OpenRouter key is not set on the backend. The rules still run.
- **AI status `rate_limited_rules_only`:** Free rate limit reached. Stop retrying; rerun with AI toggle off.
- **AI status `invalid_model_response` or `unavailable_rules_only`:** Selected free model did not return structured output, or upstream service is unavailable. Try a current explicit free chat model ID after verifying its capabilities. Don't promise live AI if it's not working in incognito.
- **Review action denied:** The demo has separate Creator and Reviewer actions; switch personas in the header.

**Never promise a certain selection outcome.** Judges decide based on their own evaluation, and the public project must be thoroughly tested before the submission deadline.
