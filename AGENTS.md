# Agent instructions — multiPersonaDemo

This repository contains **Project Apex**, a FastAPI developer velocity dashboard demo, plus supporting demo assets.

## Repository layout

```
project-apex/          # Main application (FastAPI + SQLAlchemy + dbt models)
  src/                 # Application source
  tests/               # pytest suite
  scripts/seed_data.py # Populates apex.db with demo data
  dbt/                 # dbt transformation models (not required for API/tests)
multiPersonalDemo.html # GTM demo playbook (not part of the app runtime)
```

All application work happens inside `project-apex/`.

## Cursor Cloud specific instructions

### Environment setup

Cloud agents use `.cursor/environment.json` to install dependencies on startup. The `install` command:

1. Installs Python packages from `project-apex/requirements.txt`
2. Creates `project-apex/.env` from `.env.example` if missing
3. Seeds `apex.db` with demo data (idempotent)

No secrets are required for local development — `.env.example` defaults work out of the box.

### Running tests

```bash
cd project-apex
python3 -m pytest tests/ -v
```

All 20 tests should pass. Tests use mocks and do not require a running server or seeded database.

### Seeding demo data

Required for live API endpoint demos (not for unit tests):

```bash
cd project-apex
python3 -m scripts.seed_data
```

After seeding, try:

- `GET /api/v1/metrics/velocity/jsmith` (header: `X-API-Key: dev-api-key-change-in-prod`)
- `GET /api/v1/metrics/team/platform-team/summary`

### Starting the API server

```bash
export PATH="$HOME/.local/bin:$PATH"
cd project-apex
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The dashboard is served at `http://localhost:8000/`. Health check: `GET /health`.

A dev server terminal is also configured in `.cursor/environment.json` and starts automatically in cloud agent sessions.

### Authentication

Protected routes require the `X-API-Key` header. Default key from `.env.example`:

```
X-API-Key: dev-api-key-change-in-prod
```

For production deployments, override `API_KEY` via Cursor Cloud Agents → Secrets.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./apex.db` | SQLite database |
| `WEBHOOK_SECRET` | `your-github-webhook-secret` | GitHub webhook HMAC validation |
| `API_KEY` | `dev-api-key-change-in-prod` | API authentication |

### dbt models

dbt models live in `project-apex/dbt/` but are not wired into the FastAPI runtime. They are reference/documentation artifacts for the analytics pipeline. Do not install dbt unless explicitly working on those models.

### Git workflow

- Application code lives on feature branches (e.g. `feature/ac-04-team-velocity`)
- Run tests before committing: `cd project-apex && python3 -m pytest tests/ -v`
- Keep changes scoped to `project-apex/` unless the task involves repo-level config
