# Development Workflow

## Prerequisites

- Python 3.12 (minimum supported Python is 3.11), Node.js 22, npm, Git
- PostgreSQL 16 for a production-like local run; SQLite is used by tests
- Docker Compose is optional

## Local setup

```powershell
Copy-Item .env.example .env
# Replace SECRET_KEY with a random value of at least 32 characters.
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements-dev.txt
Set-Location backend
alembic upgrade head
python ..\infrastructure\scripts\seed_demo.py
python ..\infrastructure\scripts\bootstrap_admin.py --email admin@example.com --name "Platform Admin" --password "Choose-A-Long-Password!"
uvicorn app.main:app --reload
```

Run the frontend in another terminal with Node.js 22:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` and `/health` to the backend at port 8000. Ensure `DATABASE_URL` is configured in the environment (PostgreSQL by default in `.env.example`; for SQLite use `sqlite:///./eomp.db`).

## Checks

```powershell
Set-Location backend
pytest
ruff check app tests alembic
ruff format --check app tests alembic
```

```powershell
Set-Location frontend
npm run lint
npm run build
```

Tests create an isolated SQLite database and do not require PostgreSQL, credentials, or external services. Add business-rule tests in `tests/unit` and HTTP/database contract tests in `tests/integration`.

## Pull requests

Keep changes focused, add tests for behavior, document API changes, and avoid committing environment files or generated output. Pull requests to `main` run backend CI, frontend CI and dependency/secret checks.
