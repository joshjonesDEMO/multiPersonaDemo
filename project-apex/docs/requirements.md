# Project Apex — MVP Requirements

**Product Owner:** Priya  
**Source:** [Stakeholder Kickoff](../meetings/stakeholder-kickoff.md) (2024-01-08)  
**Target:** Week 4 launch  
**Status:** Approved for Sprint 1

---

## MVP Feature Priorities

| Priority | Feature | Story ID |
|----------|---------|----------|
| P0 | GitHub webhook ingestion (PR, push, review events) | US-01 |
| P0 | Team cycle time (avg, p50, p90) — 30-day rolling window | US-02 |
| P0 | Individual developer velocity (self + manager only) | US-03 |
| P0 | Review latency (PR opened → first review) | US-04 |
| P1 | PR throughput (merged PRs per week per team) | US-05 |
| P1 | Team summary rollup endpoint | US-06 |
| P2 | Simple trend line (cycle time week over week) | US-07 |

---

## User Stories & Acceptance Criteria

### US-01: GitHub Event Ingestion

**As a** platform engineer,  
**I want** GitHub webhook events ingested and persisted,  
**So that** downstream metrics have a reliable source of truth.

**Acceptance Criteria (AC-01):**

```gherkin
Given a valid GitHub webhook payload for pull_request, push, or pull_request_review
When POST /webhooks/github is called with a valid X-Hub-Signature-256
Then the event is parsed, normalized, and persisted to developer_events or review_records
And the endpoint returns {"status": "accepted", "event_type": "<type>"}

Given an invalid or missing webhook signature when WEBHOOK_SECRET is configured
When POST /webhooks/github is called
Then the endpoint returns 401 Unauthorized
```

---

### US-02: Team Cycle Time

**As an** engineering director,  
**I want** to see my team's PR cycle time with percentile breakdowns,  
**So that** I can identify bottlenecks without relying on team averages alone.

**Acceptance Criteria (AC-02):**

```gherkin
Given a team_id matching repo prefix convention (e.g. "platform-team")
When GET /api/v1/metrics/team/{teamId}/summary?lookback_days=30 is called
Then the response includes avg_cycle_time_hours, p50_cycle_time_hours, p90_cycle_time_hours
And prs_merged reflects merged PRs within the 30-day window
And contributors lists distinct authors for that team
```

---

### US-03: Individual Developer Velocity

**As a** developer,  
**I want** to view my own velocity metrics,  
**So that** I can self-assess without being ranked against peers.

**Acceptance Criteria (AC-03):**

```gherkin
Given a valid GitHub login (user_id)
When GET /api/v1/metrics/velocity/{userId}?lookback_days=30 is called
Then the response includes prs_merged, avg_cycle_time_hours, avg_additions, avg_deletions
And access is restricted to self + direct manager (open question — see below)
```

---

### US-04: Manager Team Cycle Time View

**As an** engineering manager,  
**I want** to view my team's average PR cycle time for the last 30 days,  
**So that** I can report velocity trends in sprint reviews and stakeholder meetings.

**Acceptance Criteria (AC-04):**

```gherkin
Given I am an authenticated engineering manager
When I request team velocity for my team over the last 30 days
Then I receive avg_cycle_time_hours, p50_cycle_time_hours, and p90_cycle_time_hours
And the data reflects only merged pull requests within the lookback window
And prs_merged count is accurate for the period
And avg_review_latency_hours is included in the team summary
```

---

### US-05: Review Latency

**As an** engineering director,  
**I want** to see how long PRs wait for a first review,  
**So that** I can address review bottlenecks before releases slip.

**Acceptance Criteria (AC-05):**

```gherkin
Given review events have been ingested for a team's repos
When GET /api/v1/metrics/team/{teamId}/summary is called
Then avg_review_latency_hours reflects time from PR open to first review
And reviews_submitted counts reviews in the lookback window
```

---

### US-06: Team Summary Rollup

**As a** VP of Engineering,  
**I want** a single endpoint that rolls up team velocity and review health,  
**So that** I can answer "are our teams getting faster?" without drilling into individual stats.

**Acceptance Criteria (AC-06):**

```gherkin
Given team_id and lookback_days (default 30, max 90)
When GET /api/v1/metrics/team/{teamId}/summary is called with X-API-Key
Then the response combines cycle time percentiles and review latency in one payload
And lookback_days > 90 returns 400 Bad Request
```

---

### US-07: Weekly Trend (P2 — Deferred to v1.1)

**As an** executive,  
**I want** a simple trend line showing whether cycle time is improving week over week,  
**So that** I can report quarter-over-quarter progress.

**Acceptance Criteria (AC-07):** Deferred — dbt `fct_team_velocity_weekly` provides the data layer; API/UI in v1.1.

---

## Explicitly Deferred to v2

- Integration with Jira/Linear for story-point correlation
- Slack notifications for velocity alerts
- Benchmarking against industry data
- Mobile view
- Durable message queue (Redis Streams) — MVP uses in-process async queue

---

## Open Questions (Unresolved Before Sprint Start)

1. **Access controls:** Restrict `/velocity/{userId}` to self + manager only, or open to all authenticated users?
2. **Contractors:** Include external contractors with GitHub access in team velocity stats?
3. **Team membership:** No single source of truth — data team to maintain CSV seed in dbt; who owns updates?
4. **Merge definition:** Do squash-merges on old branches count the same as regular merges?

---

## Sprint 1 Scope (This Sprint)

| Deliverable | Owner | Status |
|-------------|-------|--------|
| Webhook ingestion + event models | Data Engineering | In progress |
| dbt staging/intermediate/mart models | Data Engineering | In progress |
| Velocity + team summary API endpoints | Developer | In progress |
| Auth middleware (X-API-Key) | Developer | Done |
| requirements.md (this document) | Product Owner | Done |
