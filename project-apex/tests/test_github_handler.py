"""
Tests for the GitHub webhook payload parser.
"""
import pytest
from datetime import datetime, timezone

from src.ingestion.github_handler import (
    parse_pull_request_event,
    parse_push_event,
    parse_review_event,
    route_event,
)


SAMPLE_PR_OPENED = {
    "action": "opened",
    "pull_request": {
        "id": 123456789,
        "number": 42,
        "title": "feat: add velocity endpoint",
        "user": {"login": "jsmith"},
        "created_at": "2024-01-15T09:00:00Z",
        # merged_at omitted — only present on closed/merged PRs (demo bug: KeyError)
        "additions": 200,
        "deletions": 45,
        "changed_files": 6,
    },
    "repository": {"full_name": "acme/platform-team-api"},
}

# Payload with explicit null merged_at (key present — parses successfully even with direct access)
SAMPLE_PR_OPENED_NULLS = {
    **SAMPLE_PR_OPENED,
    "pull_request": {
        **SAMPLE_PR_OPENED["pull_request"],
        "merged_at": None,
        "closed_at": None,
    },
}

SAMPLE_PR_MERGED = {
    "action": "closed",
    "pull_request": {
        "id": 123456790,
        "number": 43,
        "title": "fix: handle missing merged_at",
        "user": {"login": "alee"},
        "created_at": "2024-01-15T08:00:00Z",
        "merged_at": "2024-01-15T16:30:00Z",
        "closed_at": "2024-01-15T16:30:00Z",
        "additions": 12,
        "deletions": 3,
        "changed_files": 2,
    },
    "repository": {"full_name": "acme/platform-team-api"},
}

SAMPLE_REVIEW = {
    "action": "submitted",
    "review": {
        "id": 987654321,
        "user": {"login": "alee"},
        "state": "APPROVED",
        "submitted_at": "2024-01-15T11:00:00Z",
    },
    "pull_request": {
        "number": 42,
        "user": {"login": "jsmith"},
        "created_at": "2024-01-15T09:00:00Z",
    },
    "repository": {"full_name": "acme/platform-team-api"},
}


class TestParsePullRequestEvent:

    def test_opened_pr_without_merged_at_key_raises_keyerror(self):
        """Opened PRs omit merged_at — direct key access causes KeyError (demo bug)."""
        with pytest.raises(KeyError, match="merged_at"):
            parse_pull_request_event(SAMPLE_PR_OPENED)

    def test_parses_merged_pr_with_timestamps(self):
        event = parse_pull_request_event(SAMPLE_PR_MERGED)
        assert event.merged_at is not None
        assert event.merged_at.tzinfo is not None  # must be timezone-aware

    def test_parses_additions_and_deletions(self):
        event = parse_pull_request_event(SAMPLE_PR_OPENED_NULLS)
        assert event.additions == 200
        assert event.deletions == 45

    def test_repo_full_name_preserved(self):
        event = parse_pull_request_event(SAMPLE_PR_OPENED_NULLS)
        assert event.repo == "acme/platform-team-api"


class TestParseReviewEvent:

    def test_parses_state_as_lowercase(self):
        event = parse_review_event(SAMPLE_REVIEW)
        assert event.state == "approved"

    def test_review_latency_can_be_computed(self):
        event = parse_review_event(SAMPLE_REVIEW)
        latency = (event.submitted_at - event.pr_created_at).total_seconds() / 3600
        assert latency == pytest.approx(2.0, abs=0.01)


class TestRouteEvent:

    def test_routes_pull_request(self):
        result = route_event("pull_request", SAMPLE_PR_OPENED_NULLS)
        assert result is not None
        assert result.pr_number == 42

    def test_routes_review(self):
        result = route_event("pull_request_review", SAMPLE_REVIEW)
        assert result is not None

    def test_returns_none_for_unknown_event(self):
        result = route_event("marketplace_purchase", {})
        assert result is None
