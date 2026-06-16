"""
UserService: user accounts, profiles, and preferences.

Owner: Platform Team
Language: Python/FastAPI

Provides user lookup by GitHub login for AnalyticsService integration.
The internal endpoint GET /internal/users/by-github-login/{login} is the
primary integration contract with AnalyticsService.
"""
from typing import Optional


# Demo seed data — in production this would query UserService's database
_GITHUB_LOGIN_MAP: dict[str, dict] = {
    "jsmith": {
        "internal_user_id": "usr_001",
        "github_login": "jsmith",
        "display_name": "Jordan Smith",
        "manager_id": "usr_mgr_001",
        "team_id": "platform-team",
    },
    "alee": {
        "internal_user_id": "usr_002",
        "github_login": "alee",
        "display_name": "Alex Lee",
        "manager_id": "usr_mgr_001",
        "team_id": "platform-team",
    },
    "priya": {
        "internal_user_id": "usr_003",
        "github_login": "priya",
        "display_name": "Priya Patel",
        "manager_id": "usr_mgr_002",
        "team_id": "data-team",
    },
}


class UserService:
    """User accounts, profiles, and GitHub login → internal user_id mapping."""

    def get_by_github_login(self, github_login: str) -> Optional[dict]:
        """
        Look up a user by GitHub login.

        Returns internal user_id, manager hierarchy, and team membership.
        Used by AnalyticsService for /velocity/{userId} access control.
        """
        return _GITHUB_LOGIN_MAP.get(github_login.lower())

    def get_profile(self, internal_user_id: str) -> Optional[dict]:
        """Return user profile by internal ID."""
        for user in _GITHUB_LOGIN_MAP.values():
            if user["internal_user_id"] == internal_user_id:
                return user
        return None
