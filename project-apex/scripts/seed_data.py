#!/usr/bin/env python3
"""
Seed apex.db with realistic developer_events and review_records.

Run from project-apex root:
    python -m scripts.seed_data

Includes edge-case rows for demo:
- User with zero merged PRs in window (demo_user_no_prs)
- Record with merged_at=None that slips filter (for velocity_service bug demo)
"""
import asyncio
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete
from src.models.database import (
    DeveloperEvent,
    ReviewRecord,
    init_db,
    AsyncSessionLocal,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def seed() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        # Clear existing data for idempotent re-runs
        await session.execute(delete(ReviewRecord))
        await session.execute(delete(DeveloperEvent))
        await session.commit()

        now = _now()
        events: list[DeveloperEvent] = []
        reviews: list[ReviewRecord] = []

        # --- platform-team: jsmith, alee — healthy velocity data ---
        for i, (author, hours_open, hours_to_merge) in enumerate([
            ("jsmith", 10, 2),
            ("jsmith", 8, 0),
            ("jsmith", 24, 4),
            ("alee", 6, 1),
            ("alee", 12, 3),
            ("alee", 16, 5),
        ]):
            created = now - timedelta(hours=hours_open)
            merged = now - timedelta(hours=hours_to_merge)
            events.append(
                DeveloperEvent(
                    event_id=f"seed-pr-platform-{i:03d}",
                    event_type="pull_request",
                    repo="acme/platform-team-api",
                    author=author,
                    pr_number=100 + i,
                    created_at=created,
                    merged_at=merged,
                    additions=80 + i * 10,
                    deletions=20 + i,
                )
            )

        # --- data-team: priya ---
        for i in range(3):
            created = now - timedelta(days=5 + i, hours=4)
            merged = now - timedelta(days=5 + i)
            events.append(
                DeveloperEvent(
                    event_id=f"seed-pr-data-{i:03d}",
                    event_type="pull_request",
                    repo="acme/data-team-pipeline",
                    author="priya",
                    pr_number=200 + i,
                    created_at=created,
                    merged_at=merged,
                    additions=150,
                    deletions=30,
                )
            )

        # --- Edge case: user with NO merged PRs in window (Dev Step 3 scenario) ---
        events.append(
            DeveloperEvent(
                event_id="seed-pr-open-only",
                event_type="pull_request",
                repo="acme/platform-team-api",
                author="demo_user_no_prs",
                pr_number=999,
                created_at=now - timedelta(days=5),
                merged_at=None,  # still open
                additions=50,
                deletions=10,
            )
        )

        # --- Edge case: bad record with merged_at=None but passes NOT NULL filter
        #     in some edge cases — actually we need merged_at set for filter but
        #     the velocity bug is about records in result set with None merged_at.
        #     SQLAlchemy filter merged_at.isnot(None) should exclude these, but
        #     the planted bug is in list comprehension without None guard.
        #     Seed a record that WOULD cause TypeError if it got into merged_prs.
        #     We can't easily slip past SQL filter, so the bug demo uses mock in tests.
        #     For live API: jsmith has good data; demo_user_no_prs returns empty (0 PRs).

        # --- Review records for platform-team ---
        for i, (reviewer, latency_h) in enumerate([
            ("alee", 2.0),
            ("jsmith", 4.5),
            ("alee", 3.0),
            ("priya", 6.0),
        ]):
            submitted = now - timedelta(days=2, hours=i)
            reviews.append(
                ReviewRecord(
                    event_id=f"seed-review-{i:03d}",
                    pr_number=100 + i,
                    repo="acme/platform-team-api" if i < 3 else "acme/data-team-pipeline",
                    reviewer=reviewer,
                    author="jsmith" if i < 2 else "alee",
                    state="approved",
                    submitted_at=submitted,
                    review_latency_hours=latency_h,
                )
            )

        session.add_all(events)
        session.add_all(reviews)
        await session.commit()

        print(f"Seeded {len(events)} developer_events and {len(reviews)} review_records")
        print("Try: GET /api/v1/metrics/velocity/jsmith (X-API-Key: dev-api-key-change-in-prod)")
        print("Try: GET /api/v1/metrics/team/platform-team/summary")


if __name__ == "__main__":
    asyncio.run(seed())
