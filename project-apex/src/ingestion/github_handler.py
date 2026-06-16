"""
GitHub webhook payload parser.

Normalises raw GitHub API payloads into our internal event models.
Called by the webhook route before events are queued for processing.
"""
from datetime import datetime, timezone
from typing import Any, Optional

from src.ingestion.event_models import PullRequestEvent, PushEvent, ReviewEvent


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 datetime string from GitHub into a timezone-aware datetime."""
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_pull_request_event(payload: dict[str, Any]) -> PullRequestEvent:
    pr = payload["pull_request"]
    return PullRequestEvent(
        event_id=str(payload["pull_request"]["id"]),
        action=payload["action"],
        pr_number=pr["number"],
        repo=payload["repository"]["full_name"],
        author=pr["user"]["login"],
        title=pr["title"],
        created_at=_parse_dt(pr["created_at"]),
        merged_at=_parse_dt(pr.get("merged_at")),
        closed_at=_parse_dt(pr.get("closed_at")),
        additions=pr.get("additions", 0),
        deletions=pr.get("deletions", 0),
        changed_files=pr.get("changed_files", 0),
    )


def parse_push_event(payload: dict[str, Any]) -> PushEvent:
    return PushEvent(
        event_id=f"{payload['repository']['id']}-{payload['after']}",
        repo=payload["repository"]["full_name"],
        pusher=payload["pusher"]["name"],
        ref=payload["ref"],
        commit_count=len(payload.get("commits", [])),
        pushed_at=datetime.now(timezone.utc),
    )


def parse_review_event(payload: dict[str, Any]) -> ReviewEvent:
    review = payload["review"]
    pr = payload["pull_request"]
    return ReviewEvent(
        event_id=str(review["id"]),
        pr_number=pr["number"],
        repo=payload["repository"]["full_name"],
        reviewer=review["user"]["login"],
        author=pr["user"]["login"],
        state=review["state"].lower(),
        submitted_at=_parse_dt(review["submitted_at"]),
        pr_created_at=_parse_dt(pr["created_at"]),
    )


def route_event(event_type: str, payload: dict[str, Any]):
    """
    Route a raw GitHub webhook payload to the correct parser.
    Returns a normalised event model or None if the event type is unrecognised.
    """
    if event_type == "pull_request":
        return parse_pull_request_event(payload)
    if event_type == "push":
        return parse_push_event(payload)
    if event_type == "pull_request_review":
        return parse_review_event(payload)
    return None
