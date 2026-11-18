# OpenRouter AI advisory — implementation notes

- OpenRouter endpoint: `POST https://openrouter.ai/api/v1/chat/completions`.
- API key: backend environment variable `OPENROUTER_API_KEY`; required **only** for remote LLM assistance.
- Model: `OPENROUTER_MODEL`, default `openrouter/free`; explicit model IDs are accepted.
- Cost target: free variants. Model pricing and rate limits can change; confirm at https://openrouter.ai/collections/free-models.
- The deterministic checker in `backend/app/rules.py` is always executed regardless of model configuration or availability.
- `backend/app/ai.py` calls OpenRouter using httpx; no OpenAI credentials or client are required.
- Marketing copy is passed as **data** to a system prompt. Approved source IDs, kinds, and bodies are sent only for the current demo session.
- Model findings are *not* trusted automatically: server verifies that source code exists and is active, quote is an exact excerpt from submitted text, severity/status match allowed values, and contradiction citations refer to a fact. Source text in the final finding comes from the database. Invalid items are dropped.
- Common statuses: `not_configured`, `skipped_by_user`, `completed`, `rate_limited_rules_only`, `demo_limit_rules_only`, `unavailable_rules_only`, `invalid_model_response`, `key_rejected_rules_only`.
- The React editor displays whether AI is configured, the model name, an opt-out switch, and the actual analysis mode attached to the current review.
- Default provider-usage guards (single instance): `AI_DEMO_DAILY_LIMIT=35`, `AI_DEMO_SESSION_LIMIT=4`. They are in-memory, not distributed, and not a substitute for account-level spend limits.
- Provider/model may retain inputs; use fictional, non-sensitive content only. OpenRouter rate-limit failures may count against the provider's free quota.
- No automated publishing or approval, and no unsupported promise that every model result is correct.

## Offline test coverage

`backend/tests/test_openrouter.py` includes tests of:
1. Key missing → rules-only.
2. Explicit opt-out → zero provider calls.
3. Valid excerpt/source response → accepted, matching stored fact/policy.
4. Invented source/excerpt → rejected.
5. Provider 429 and local per-session/global quota → labelled fallback.
6. Existing analysis endpoint with `use_ai=false` → deterministic findings and correct engine status.

No test needs a real network call or real key. For a live API smoke test, create a valid OpenRouter key locally, choose a current eligible model and run an example in the app.
