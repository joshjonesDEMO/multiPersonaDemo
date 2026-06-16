# Project Apex — Developer Velocity Dashboard

Internal platform team project. Ingests signals from GitHub, CI/CD, and code review tools
to surface developer productivity metrics: cycle time, throughput, review depth.

## Stack

- **API**: FastAPI + Python 3.11
- **Data models**: SQLAlchemy 2.0
- **Transformations**: dbt
- **Tests**: pytest + pytest-asyncio
- **Events**: GitHub Webhooks → async queue → AnalyticsService

## Services

| Service | Responsibility |
|---|---|
| `webhooks` | Ingest GitHub events via POST /webhooks/github |
| `velocity_service` | Calculate cycle time, throughput, review latency |
| `event_processor` | Async fan-out for incoming webhook events |
| `github_handler` | Parse and normalize raw GitHub webhook payloads |

## API Endpoints

```
POST /webhooks/github              — Ingest GitHub webhook events
GET  /api/v1/metrics/velocity/{userId}    — 30-day developer velocity
GET  /api/v1/metrics/team/{teamId}/summary — Team rollup (cycle time, throughput)
GET  /health                       — Health check
```

## Running locally

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
```

## Running tests

```bash
pytest tests/ -v
```

## dbt models

```
staging/    stg_github_events          — clean and type-cast raw events
intermediate/ int_developer_daily      — PR metrics per developer per day
marts/      fct_team_velocity_weekly   — cycle time, throughput per team per week
```
