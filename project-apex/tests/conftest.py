"""
Shared pytest fixtures for Project Apex tests.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.ingestion.event_models import PullRequestEvent, ReviewEvent
from src.models.database import DeveloperEvent, ReviewRecord


def make_pr_event(
    event_id: str = "pr-001",
    author: str = "jsmith",
    repo: str = "acme/platform-team-api",
    pr_number: int = 42,
    created_at: datetime = None,
    merged_at: datetime = ...,  # sentinel: use default; pass None explicitly for bug tests
    additions: int = 120,
    deletions: int = 30,
) -> DeveloperEvent:
    """Factory for DeveloperEvent records in tests."""
    now = datetime.now(timezone.utc)
    if merged_at is ...:
        resolved_merged_at = now
    else:
        resolved_merged_at = merged_at
    return DeveloperEvent(
        event_id=event_id,
        event_type="pull_request",
        repo=repo,
        author=author,
        pr_number=pr_number,
        created_at=created_at or (now - timedelta(hours=8)),
        merged_at=resolved_merged_at,
        additions=additions,
        deletions=deletions,
    )


def make_review_event(
    event_id: str = "review-001",
    pr_number: int = 42,
    repo: str = "acme/platform-team-api",
    reviewer: str = "alee",
    author: str = "jsmith",
    state: str = "approved",
    latency_hours: float = 4.5,
) -> ReviewRecord:
    """Factory for ReviewRecord records in tests."""
    now = datetime.now(timezone.utc)
    return ReviewRecord(
        event_id=event_id,
        pr_number=pr_number,
        repo=repo,
        reviewer=reviewer,
        author=author,
        state=state,
        submitted_at=now,
        review_latency_hours=latency_hours,
    )


@pytest.fixture
def mock_db():
    """Return a mock AsyncSession with a chainable execute() result."""
    db = AsyncMock(spec=AsyncSession)
    return db


def make_mock_result(rows: list):
    """Wrap a list of ORM objects in a mock that behaves like a SQLAlchemy result."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    return result
