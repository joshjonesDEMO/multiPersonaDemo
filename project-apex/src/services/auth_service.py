"""
AuthService: JWT issuance, API key validation, and session management.

Owner: Security Team
Language: Python/FastAPI

AuthMiddleware in src/auth/middleware.py follows the same pattern used by
UserService and NotificationService — a copy-pasted X-API-Key validator.
AnalyticsService reuses this middleware for API authentication.
"""
import os
from typing import Optional


class AuthService:
    """JWT issuance, API key validation, session management."""

    def validate_api_key(self, api_key: Optional[str]) -> bool:
        """Validate an API key against the configured secret."""
        expected = os.getenv("API_KEY", "dev-api-key-change-in-prod")
        return api_key is not None and api_key == expected

    def issue_jwt(self, user_id: str, expires_hours: int = 24) -> str:
        """
        Issue a JWT for authenticated sessions.

        NOTE: MVP uses API keys only. JWT issuance is stubbed for future
        UserService integration.
        """
        return f"stub-jwt-{user_id}-{expires_hours}h"
