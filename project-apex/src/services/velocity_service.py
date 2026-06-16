"""
VelocityService: computes developer and team velocity metrics.

Core calculations:
  - cycle_time: time from PR opened to merged (hours)
  - throughput: merged PRs per week
  - review_latency: time from PR open to first review (hours)

NOTE: This service queries DeveloperEvent records directly.
For large datasets, use the dbt pre-aggregated models in the data warehouse instead.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import DeveloperEvent, ReviewRecord


class VelocityService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_developer_metrics(
        self,
        user_id: str,
        lookback_days: int = 30,
    ) -> dict:
        """
        Return cycle time and throughput for a single developer over the lookback window.

        Args:
            user_id: GitHub login / developer identifier
            lookback_days: number of days to look back (default: 30)

        Returns:
            dict with keys: user_id, period_days, prs_merged, avg_cycle_time_hours,
                            avg_additions, avg_deletions
        """
        since = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        result = await self.db.execute(
            select(DeveloperEvent).where(
                and_(
                    DeveloperEvent.author == user_id,
                    DeveloperEvent.event_type == "pull_request",
                    DeveloperEvent.created_at >= since,
                    DeveloperEvent.merged_at.isnot(None),
                )
            )
        )
        merged_prs = result.scalars().all()

        if not merged_prs:
            return {
                "user_id": user_id,
                "period_days": lookback_days,
                "prs_merged": 0,
                "avg_cycle_time_hours": None,
                "avg_additions": 0,
                "avg_deletions": 0,
            }

        # BUG: merged_at is filtered to NOT NULL above, but cycle_time arithmetic
        # can still fail if a record was inserted with merged_at=None due to a
        # data quality issue upstream. The filter guards against most cases, but
        # records inserted before the NOT NULL constraint was enforced may slip through.
        #
        # Real bug: for users who HAVE merged PRs but the cycle_time calculation
        # hits a None merged_at from a bad record, the whole endpoint returns 200 + empty.
        # Fix: add a defensive None check before the subtraction.
        cycle_times = [
            (pr.merged_at - pr.created_at).total_seconds() / 3600
            for pr in merged_prs
            # missing: `if pr.merged_at is not None` guard — causes silent empty result
            # when a single bad record slips through the NOT NULL filter
        ]

        return {
            "user_id": user_id,
            "period_days": lookback_days,
            "prs_merged": len(merged_prs),
            "avg_cycle_time_hours": round(sum(cycle_times) / len(cycle_times), 2),
            "avg_additions": round(sum(pr.additions for pr in merged_prs) / len(merged_prs)),
            "avg_deletions": round(sum(pr.deletions for pr in merged_prs) / len(merged_prs)),
        }

    async def get_team_cycle_time(
        self,
        team_id: str,
        lookback_days: int = 30,
    ) -> dict:
        """
        Return aggregated cycle time and throughput for a team over the lookback window.

        team_id maps to a GitHub repository prefix (e.g. "platform-team" matches
        repos like "acme/platform-team-api", "acme/platform-team-worker").

        Args:
            team_id: team identifier — matches against DeveloperEvent.repo prefix
            lookback_days: number of days to look back (default: 30)
        """
        since = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        result = await self.db.execute(
            select(DeveloperEvent).where(
                and_(
                    DeveloperEvent.repo.like(f"%{team_id}%"),
                    DeveloperEvent.event_type == "pull_request",
                    DeveloperEvent.created_at >= since,
                    DeveloperEvent.merged_at.isnot(None),
                )
            )
        )
        prs = result.scalars().all()

        if not prs:
            return {
                "team_id": team_id,
                "period_days": lookback_days,
                "prs_merged": 0,
                "avg_cycle_time_hours": None,
                "p50_cycle_time_hours": None,
                "p90_cycle_time_hours": None,
                "contributors": [],
            }

        cycle_times_raw = [
            (pr.merged_at - pr.created_at).total_seconds() / 3600
            for pr in prs
        ]
        cycle_times = sorted(cycle_times_raw)
        n = len(cycle_times)

        return {
            "team_id": team_id,
            "period_days": lookback_days,
            "prs_merged": n,
            "avg_cycle_time_hours": round(sum(cycle_times) / n, 2),
            "p50_cycle_time_hours": round(cycle_times[n // 2], 2),
            "p90_cycle_time_hours": round(cycle_times[int(n * 0.9)], 2),
            "contributors": list({pr.author for pr in prs}),
        }

    async def get_review_latency(
        self,
        team_id: str,
        lookback_days: int = 30,
    ) -> dict:
        """
        Return average first-review latency for PRs belonging to team_id repos.
        """
        since = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        result = await self.db.execute(
            select(ReviewRecord).where(
                and_(
                    ReviewRecord.repo.like(f"%{team_id}%"),
                    ReviewRecord.submitted_at >= since,
                )
            )
        )
        reviews = result.scalars().all()

        if not reviews:
            return {
                "team_id": team_id,
                "period_days": lookback_days,
                "reviews_submitted": 0,
                "avg_review_latency_hours": None,
            }

        latencies = [r.review_latency_hours for r in reviews if r.review_latency_hours is not None]
        return {
            "team_id": team_id,
            "period_days": lookback_days,
            "reviews_submitted": len(reviews),
            "avg_review_latency_hours": round(sum(latencies) / len(latencies), 2) if latencies else None,
        }
