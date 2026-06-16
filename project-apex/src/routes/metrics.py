"""
Developer and team velocity metrics endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import get_db
from src.services.velocity_service import VelocityService

router = APIRouter()


@router.get("/velocity/{user_id}")
async def get_developer_velocity(
    user_id: str,
    lookback_days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """
    Return 30-day velocity metrics for a single developer.

    - **user_id**: GitHub login (e.g. "jsmith")
    - **lookback_days**: window size in days (default: 30, max: 90)
    """
    if lookback_days > 90:
        raise HTTPException(status_code=400, detail="lookback_days cannot exceed 90")

    svc = VelocityService(db)
    return await svc.get_developer_metrics(user_id, lookback_days)


@router.get("/team/{team_id}/summary")
async def get_team_summary(
    team_id: str,
    lookback_days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """
    Return aggregated velocity and review latency for a team.

    - **team_id**: team identifier matching the repo prefix convention
    - **lookback_days**: window size in days (default: 30, max: 90)
    """
    if lookback_days > 90:
        raise HTTPException(status_code=400, detail="lookback_days cannot exceed 90")

    svc = VelocityService(db)
    cycle_time = await svc.get_team_cycle_time(team_id, lookback_days)
    review_latency = await svc.get_review_latency(team_id, lookback_days)

    return {
        **cycle_time,
        "avg_review_latency_hours": review_latency["avg_review_latency_hours"],
        "reviews_submitted": review_latency["reviews_submitted"],
    }
