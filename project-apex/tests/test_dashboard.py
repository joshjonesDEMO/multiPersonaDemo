"""Tests for the dashboard root route (GET /)."""
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_dashboard_served_at_root_without_api_key():
    """Root serves the dashboard HTML and is exempt from API-key auth."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Project Apex" in response.text
    assert "Developer Velocity Dashboard" in response.text


@pytest.mark.asyncio
async def test_protected_route_still_requires_api_key():
    """Adding / to the unprotected set must not open up the API routes."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/metrics/velocity/jsmith")

    assert response.status_code == 401
    assert "api key" in response.json()["detail"].lower()
