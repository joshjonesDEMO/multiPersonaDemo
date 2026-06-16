---
name: run-apex
description: Set up and run the Project Apex FastAPI velocity dashboard locally — creates a virtualenv, installs dependencies, seeds the demo database, and starts uvicorn. Use when the user wants to run, start, serve, or boot Project Apex locally.
disable-model-invocation: true
---

# Run Project Apex Locally

Boots the Project Apex developer velocity dashboard for local demos.

## Steps

Run from the `project-apex/` directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp -n .env.example .env
.venv/bin/python -m scripts.seed_data
.venv/bin/uvicorn src.main:app --reload --port 8000
```

Start uvicorn in the background so the terminal stays free. If `.venv` already exists, reuse it and skip creation.

## Verify

- Dashboard: open http://127.0.0.1:8000/
- Health: `curl http://127.0.0.1:8000/health` → `{"status":"ok","service":"project-apex"}`
- API requires the key:
  `curl -H "X-API-Key: dev-api-key-change-in-prod" http://127.0.0.1:8000/api/v1/metrics/velocity/jsmith`

## Seeded demo data

- Developers: `jsmith`, `alee`, `priya`
- Teams: `platform-team`, `data-team`
