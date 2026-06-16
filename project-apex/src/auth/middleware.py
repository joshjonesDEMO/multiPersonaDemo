"""
Simple API key authentication middleware.
All routes except /health require a valid X-API-Key header.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import os

UNPROTECTED_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in UNPROTECTED_PATHS:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        expected = os.getenv("API_KEY", "dev-api-key-change-in-prod")

        if not api_key or api_key != expected:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key"},
            )

        return await call_next(request)
