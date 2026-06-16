"""
Pydantic models for normalised GitHub webhook events.
Raw payloads from GitHub are parsed here before being stored or processed.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PullRequestEvent(BaseModel):
    event_id: str
    action: str                  # opened | closed | reopened | review_requested
    pr_number: int
    repo: str
    author: str
    title: str
    created_at: datetime
    merged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    review_requested_at: Optional[datetime] = None


class PushEvent(BaseModel):
    event_id: str
    repo: str
    pusher: str
    ref: str                     # refs/heads/main
    commit_count: int
    pushed_at: datetime


class ReviewEvent(BaseModel):
    event_id: str
    pr_number: int
    repo: str
    reviewer: str
    author: str
    state: str                   # approved | changes_requested | commented
    submitted_at: datetime
    pr_created_at: datetime      # needed to compute review latency
