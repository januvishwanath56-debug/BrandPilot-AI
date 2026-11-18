# Versioned Git workflow

All functional implementation commits must occur during the event's official build window (16 November 2026, 10:00 AM IST to 19 November 2026, 10:00 AM IST). Planning materials prepared earlier are allowed and should be labelled as planning.

## Suggested milestone history
1. `feat: initialize BrandPilot AI functional MVP`
2. `feat: introduce source-backed brand review`
3. `feat: add revision and reviewer workflow`
4. `test: add acceptance and integration tests`
5. `feat: deploy public demo and document setup`
6. `docs: prepare round 2 submission evidence`

## Local workflow after implementing the first milestone
```
git init
git add .
git commit -m "feat: initialize BrandPilot AI functional MVP"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/BrandPilotAI.git
git push -u origin main
```

Create an empty GitHub repository named `BrandPilotAI` before adding the remote. Use real commit messages matching actual completed changes, and never misrepresent commit dates. Protect `.env`, database files, `node_modules`, local Python environments and provider credentials via `.gitignore`.
