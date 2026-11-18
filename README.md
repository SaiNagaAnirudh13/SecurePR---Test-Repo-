# Enterprise Order Management Platform (EOMP)

EOMP is a corporate-style order and fulfillment platform starter for customer account management, product catalog, warehouse inventory, order lifecycle, payment intent abstraction, shipment tracking, audit history, reporting and asynchronous notifications. It is designed as a realistic, testable target for engineering and Pull Request review.

> **Scope:** This repository demonstrates application architecture and business workflows. Tax, payment settlement, notification delivery, and production identity controls are intentionally simplified and must be integrated and reviewed before production use.

## Architecture

The backend is a modular FastAPI application using SQLAlchemy 2, Pydantic, Alembic and PostgreSQL. A React/TypeScript operations console consumes the versioned REST API. Order placement is transactional: customer/product validation, stock reservation, price snapshots, audit history, and notification outbox records are committed together. A separate worker processes queued notification records. See [architecture](docs/architecture.md), [API design](docs/api.md), [security](docs/security.md), [development workflow](docs/development.md), and [operations](docs/operations.md).

## Repository structure

```text
backend/
  app/api/          Versioned routers and authorization dependencies
  app/core/         Settings, database, security, logging and errors
  app/models/       Relational entities
  app/repositories/ Persistence query helpers
  app/schemas/      Validated request/response contracts
  app/services/     Order, audit and notification workflows
  alembic/          Schema migration environment and initial revision
  tests/            Unit and integration suites
frontend/
  src/components/   Navigation, data states, reusable page elements
  src/hooks/        API resource loading
  src/pages/         Login, dashboard and operational views
  src/services/      Typed API client
infrastructure/
  docker/           Backend and frontend container builds
  scripts/          Admin bootstrap and demo data
docs/               Architecture, API, security, development, operations
.github/workflows/  Backend CI, frontend CI, security checks
```

## Prerequisites

- Python 3.12 (code supports Python 3.10+)
- Node.js 22 and npm
- PostgreSQL 16 for local production-like use, or Docker Compose

## Local setup

```powershell
Copy-Item .env.example .env
# Set SECRET_KEY to a random string of at least 32 characters.
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements-dev.txt
Set-Location backend
alembic upgrade head
python ..\infrastructure\scripts\seed_demo.py
python ..\infrastructure\scripts\bootstrap_admin.py --email admin@example.com --name "Platform Admin" --password "Choose-A-Long-Password!"
uvicorn app.main:app --reload
```

The `.env.example` targets PostgreSQL. To use SQLite locally, set `DATABASE_URL=sqlite:///./eomp.db`. In a second terminal:

```powershell
Set-Location frontend
npm ci
npm run dev
```

The console is at `http://localhost:5173`, the API at `http://localhost:8000`, and interactive API docs at `http://localhost:8000/docs`. Vite proxies API and health requests to the backend. Compose is also available with `docker compose up --build` after creating `.env`.

## Configuration

See [.env.example](.env.example). Settings include `APP_ENV`, `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`, `LOG_LEVEL`, and `WORKER_POLL_SECONDS`. Production requires a secret key of at least 32 characters and rejects the development-only default. Do not commit `.env`, production credentials, or private keys.

## Tests and quality

Backend tests use an isolated in-memory SQLite database:

```powershell
Set-Location backend
pytest
ruff check app tests alembic
ruff format --check app tests alembic
```

Frontend:

```powershell
Set-Location frontend
npm ci
npm run lint
npm run build
```

## CI/CD

Pull requests targeting `main` run Python dependency installation, Ruff checks, pytest, TypeScript/ESLint checks and a Vite production build. A separate security workflow audits Python and npm dependencies and scans repository history for secrets. Workflows require no user-managed deployment credentials.

## Intentionally simplified components

Tax is a fixed illustrative rate; stock reservation uses the first matching warehouse; payment endpoints create pending provider-neutral intents and never process sensitive payment data; notifications are logged by the worker rather than sent externally. Account recovery, advanced rate limiting, secure-cookie sessions, and external observability integrations are production hardening items. See [operations](docs/operations.md) and [security](docs/security.md).

## SecurePR CI Integration Test
Testing dynamic GitHub CI discovery.

## CI Integration Test Update
Testing SecurePR automated review with a small README change.
