from typing import Any, Dict

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class LaravelAuthService:
    """Service that proxies Sanctum authentication checks to Laravel API."""

    def __init__(self) -> None:
        self.base_url = settings.LARAVEL_BASE_URL.rstrip("/")
        self.login_endpoint = settings.LARAVEL_LOGIN_ENDPOINT
        self.me_endpoint = settings.LARAVEL_ME_ENDPOINT
        self.timeout = settings.LARAVEL_TIMEOUT_SECONDS

    async def login(
        self,
        password: str,
        username: str | None = None,
        email: str | None = None,
    ) -> Dict[str, Any]:
        payload = {"password": password}
        if username:
            payload["username"] = username
        elif email:
            payload["email"] = email

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}{self.login_endpoint}", json=payload)

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Laravel login failed",
            )

        data = response.json()
        token = data.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Laravel response did not include a token",
            )
        return data

    async def validate_token(self, token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{self.me_endpoint}", headers=headers)

        if response.status_code in {401, 403}:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Sanctum token",
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to validate token with Laravel",
            )

        data = response.json()
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
            user = data["data"]
        elif isinstance(data, dict):
            user = data
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unexpected response format from Laravel",
            )

        user_id = user.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Laravel token validated but user id is missing",
            )

        return user


laravel_auth_service = LaravelAuthService()
