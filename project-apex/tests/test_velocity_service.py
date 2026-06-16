"""
Tests for VelocityService.

Status: PARTIAL — happy-path coverage only.
Missing: edge cases for empty dataset, single contributor, 30-day boundary behaviour.
These are intentionally left incomplete for the demo (TDD use case).
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta

from src.services.velocity_service import VelocityService
from tests.conftest import make_pr_event, make_review_event, make_mock_result


class TestGetDeveloperMetrics:

    @pytest.mark.asyncio
    async def test_returns_correct_avg_cycle_time(self, mock_db):
        """Developer with two merged PRs — avg cycle time should be 8h."""
        now = datetime.now(timezone.utc)
        prs = [
            make_pr_event(
                event_id="pr-001",
                created_at=now - timedelta(hours=10),
                merged_at=now - timedelta(hours=2),
            ),
            make_pr_event(
                event_id="pr-002",
                created_at=now - timedelta(hours=8),
                merged_at=now,
            ),
        ]
        mock_db.execute.return_value = make_mock_result(prs)

        svc = VelocityService(mock_db)
        result = await svc.get_developer_metrics("jsmith")

        assert result["prs_merged"] == 2
        assert result["avg_cycle_time_hours"] == 8.0

    @pytest.mark.asyncio
    async def test_returns_pr_count_and_code_churn(self, mock_db):
        """Verify additions/deletions averages are included in the response."""
        now = datetime.now(timezone.utc)
        prs = [
            make_pr_event(event_id="pr-001", additions=200, deletions=50),
            make_pr_event(event_id="pr-002", additions=100, deletions=10),
        ]
        mock_db.execute.return_value = make_mock_result(prs)

        svc = VelocityService(mock_db)
        result = await svc.get_developer_metrics("jsmith")

        assert result["avg_additions"] == 150
        assert result["avg_deletions"] == 30

    @pytest.mark.asyncio
    async def test_none_merged_at_in_result_set_raises_typeerror(self, mock_db):
        """
        Demo bug: merged_at=None in result set causes TypeError in cycle_time calc.
        Fix: add `if pr.merged_at is not None` guard in list comprehension.
        """
        now = datetime.now(timezone.utc)
        prs = [
            make_pr_event(event_id="pr-good", merged_at=now),
            make_pr_event(event_id="pr-bad", merged_at=None),
        ]
        mock_db.execute.return_value = make_mock_result(prs)

        svc = VelocityService(mock_db)
        with pytest.raises(TypeError):
            await svc.get_developer_metrics("jsmith")

    # -----------------------------------------------------------------------
    # TODO: Add tests for the following cases (demo: TDD prompt)
    # -----------------------------------------------------------------------

    # @pytest.mark.asyncio
    # async def test_empty_dataset_returns_zero_metrics(self, mock_db):
    #     """Developer with no merged PRs in window — prs_merged=0, cycle_time=None."""
    #     pass

    # @pytest.mark.asyncio
    # async def test_single_contributor(self, mock_db):
    #     """Single PR merged — no division edge cases, avg == that PR's cycle time."""
    #     pass

    # @pytest.mark.asyncio
    # async def test_30_day_boundary_excludes_older_prs(self, mock_db):
    #     """PRs merged exactly 30 days + 1 second ago should NOT appear in results."""
    #     pass


class TestGetTeamCycleTime:

    @pytest.mark.asyncio
    async def test_team_summary_includes_percentiles(self, mock_db):
        """p50 and p90 cycle times should be present in the team summary."""
        now = datetime.now(timezone.utc)
        prs = [
            make_pr_event(
                event_id=f"pr-{i:03d}",
                repo="acme/platform-team-api",
                created_at=now - timedelta(hours=h + 2),
                merged_at=now - timedelta(hours=h),
            )
            for i, h in enumerate([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
        ]
        mock_db.execute.return_value = make_mock_result(prs)

        svc = VelocityService(mock_db)
        result = await svc.get_team_cycle_time("platform-team")

        assert "p50_cycle_time_hours" in result
        assert "p90_cycle_time_hours" in result
        assert result["prs_merged"] == 10

    @pytest.mark.asyncio
    async def test_contributors_list_is_deduplicated(self, mock_db):
        """Same author across multiple PRs should appear once in contributors."""
        now = datetime.now(timezone.utc)
        prs = [
            make_pr_event(event_id="pr-001", author="jsmith"),
            make_pr_event(event_id="pr-002", author="jsmith"),
            make_pr_event(event_id="pr-003", author="alee"),
        ]
        mock_db.execute.return_value = make_mock_result(prs)

        svc = VelocityService(mock_db)
        result = await svc.get_team_cycle_time("platform-team")

        assert len(result["contributors"]) == 2
        assert set(result["contributors"]) == {"jsmith", "alee"}

    # TODO: test_empty_team_returns_none_percentiles
    # TODO: test_lookback_days_respected


class TestGetReviewLatency:

    @pytest.mark.asyncio
    async def test_avg_review_latency_calculated_correctly(self, mock_db):
        reviews = [
            make_review_event(event_id="r-001", latency_hours=4.0),
            make_review_event(event_id="r-002", latency_hours=8.0),
        ]
        mock_db.execute.return_value = make_mock_result(reviews)

        svc = VelocityService(mock_db)
        result = await svc.get_review_latency("platform-team")

        assert result["avg_review_latency_hours"] == 6.0
        assert result["reviews_submitted"] == 2

    # TODO: test_null_latency_records_excluded_from_average
    # TODO: test_empty_reviews_returns_none_avg
