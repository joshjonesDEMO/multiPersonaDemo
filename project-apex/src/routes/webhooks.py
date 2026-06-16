"""
GitHub webhook ingestion endpoint.

Validates the incoming payload, parses it into a normalised event model,
persists it to the database, and queues it for async processing.
"""
import hashlib
import hmac
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Header, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.ingestion.github_handler import route_event
from src.ingestion.event_models import PullRequestEvent, ReviewEvent
from src.ingestion.event_processor import enqueue_event
from src.models.database import DeveloperEvent, ReviewRecord, get_db

router = APIRouter()


def _verify_signature(payload_body: bytes, signature: str) -> bool:
    """Validate the X-Hub-Signature-256 header from GitHub."""
    secret = os.getenv("WEBHOOK_SECRET", "").encode()
    expected = "sha256=" + hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def ingest_github_event(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_github_event: str = Header(...),
    x_hub_signature_256: str = Header(default=""),
):
    """
    Receive and persist GitHub webhook events.

    Supported event types: pull_request, push, pull_request_review
    """
    body = await request.body()

    secret = os.getenv("WEBHOOK_SECRET")
    if secret and not _verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload: dict[str, Any] = await request.json()
    event = route_event(x_github_event, payload)

    if event is None:
        return {"status": "ignored", "event_type": x_github_event}

    if isinstance(event, PullRequestEvent):
        record = DeveloperEvent(
            event_id=event.event_id,
            event_type="pull_request",
            repo=event.repo,
            author=event.author,
            pr_number=event.pr_number,
            created_at=event.created_at,
            merged_at=event.merged_at,
            closed_at=event.closed_at,
            additions=event.additions,
            deletions=event.deletions,
        )
        db.add(record)
        await db.commit()
        await enqueue_event(event)

    elif isinstance(event, ReviewEvent):
        latency = (
            (event.submitted_at - event.pr_created_at).total_seconds() / 3600
        )
        record = ReviewRecord(
            event_id=event.event_id,
            pr_number=event.pr_number,
            repo=event.repo,
            reviewer=event.reviewer,
            author=event.author,
            state=event.state,
            submitted_at=event.submitted_at,
            review_latency_hours=round(latency, 2),
        )
        db.add(record)
        await db.commit()
        await enqueue_event(event)

    return {"status": "accepted", "event_type": x_github_event}
