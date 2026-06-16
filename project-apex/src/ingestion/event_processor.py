"""
Async event processor for GitHub webhook fan-out.

Uses an in-process asyncio.Queue for MVP throughput (<1,000 events/day).
Events are queued after DB persistence for downstream processing (e.g.
dbt refresh triggers, notification hooks).

NOTE: Not durable — events are lost on process restart. Redis Streams
planned for v2 per ADR-001.
"""
import asyncio
import logging
from typing import Any, Optional, Union

from src.ingestion.event_models import PullRequestEvent, PushEvent, ReviewEvent

logger = logging.getLogger(__name__)

_event_queue: Optional[asyncio.Queue] = None
_processor_task: Optional[asyncio.Task] = None


def get_event_queue() -> asyncio.Queue:
    """Return the global event queue, creating it if needed."""
    global _event_queue
    if _event_queue is None:
        _event_queue = asyncio.Queue()
    return _event_queue


async def enqueue_event(event: Union[PullRequestEvent, PushEvent, ReviewEvent]) -> None:
    """Queue a normalized event for async processing."""
    queue = get_event_queue()
    await queue.put(event)
    logger.debug("Enqueued event %s", getattr(event, "event_id", "unknown"))


async def _process_events() -> None:
    """Background worker: consume events from the queue."""
    queue = get_event_queue()
    while True:
        try:
            event = await queue.get()
            event_id = getattr(event, "event_id", "unknown")
            event_type = type(event).__name__
            logger.info("Processing event %s (%s)", event_id, event_type)
            # MVP: no downstream actions yet — placeholder for dbt trigger, notifications
            queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception("Event processing failed: %s", e)


async def start_event_processor() -> None:
    """Start the background event processor task."""
    global _processor_task
    if _processor_task is None or _processor_task.done():
        _processor_task = asyncio.create_task(_process_events())
        logger.info("Event processor started")


async def stop_event_processor() -> None:
    """Stop the background event processor."""
    global _processor_task
    if _processor_task and not _processor_task.done():
        _processor_task.cancel()
        try:
            await _processor_task
        except asyncio.CancelledError:
            pass
        _processor_task = None
        logger.info("Event processor stopped")
