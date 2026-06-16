"""Tests for internal user lookup endpoint."""
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def api_key():
    return "dev-api-key-change-in-prod"


@pytest.mark.asyncio
async def test_get_user_by_github_login_found(api_key):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": api_key},
    ) as client:
        response = await client.get("/internal/users/by-github-login/jsmith")

    assert response.status_code == 200
    data = response.json()
    assert data["github_login"] == "jsmith"
    assert data["internal_user_id"] == "usr_001"
    assert data["team_id"] == "platform-team"
    assert "manager_id" in data


@pytest.mark.asyncio
async def test_get_user_by_github_login_not_found(api_key):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": api_key},
    ) as client:
        response = await client.get("/internal/users/by-github-login/unknown_user")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_user_by_github_login_case_insensitive(api_key):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": api_key},
    ) as client:
        response = await client.get("/internal/users/by-github-login/JSMITH")

    assert response.status_code == 200
    assert response.json()["github_login"] == "jsmith"
