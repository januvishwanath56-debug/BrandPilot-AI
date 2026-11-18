# Toolchain plan (research before implementation)

## Local Windows development
- Python 3.11+ with `venv`; the user's existing Python 3.11 environment is suitable.
- Node.js compatible with Vite 7 (20.19+ or 22.12+ according to Vite documentation).
- Git and a public GitHub repository.
- VS Code or any editor.

## Planned frontend dependencies
- React and React DOM (JSX, **not** TypeScript).
- Vite with React plugin for local dev server and production compilation.
- Lucide icons as an optional UI package.

## Planned backend dependencies
- FastAPI, Uvicorn, SQLAlchemy 2, Pydantic v2.
- SQLite built into Python for local development; psycopg for remote PostgreSQL.
- PyMuPDF / python-docx / python-multipart for supported document text extraction.
- Optional OpenRouter chat completions adapter via httpx; its key stays on the backend and is not required for local rules.
- pytest and FastAPI TestClient/httpx for validation.

## Environment strategy
- Local frontend accesses `/api` and Vite proxies requests to port 8000.
- Production app can serve compiled frontend and backend from a single origin.
- `.env.example` documents configuration without exposing credentials.
- `.gitignore` excludes secrets, local DBs, compiled assets and virtual environments.

## Sources checked during planning
- Vite Getting Started: https://vite.dev/guide/
- FastAPI SQL Databases: https://fastapi.tiangolo.com/tutorial/sql-databases/
- FastAPI Request Files: https://fastapi.tiangolo.com/tutorial/request-files/
- OpenRouter API: https://openrouter.ai/developers
- Render web services and free tier: https://render.com/docs/web-services and https://render.com/docs/free
