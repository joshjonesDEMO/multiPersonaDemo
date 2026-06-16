"""
Internal user lookup endpoints for service-to-service integration.

Marked internal-only — not in public API docs.
"""
from fastapi import APIRouter, HTTPException

from src.services.user_service import UserService

router = APIRouter(prefix="/internal/users", tags=["Internal"])


@router.get("/by-github-login/{login}")
async def get_user_by_github_login(login: str):
    """
    Look up internal user_id and manager hierarchy by GitHub login.

    Used by AnalyticsService for /velocity/{userId} access control.
    Internal-only endpoint — not exposed in public OpenAPI docs.
    """
    svc = UserService()
    user = svc.get_by_github_login(login)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User not found for GitHub login: {login}")
    return user
