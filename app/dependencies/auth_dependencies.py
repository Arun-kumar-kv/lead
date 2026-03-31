from fastapi import Header, HTTPException, status

from app.schemas.auth_schemas import AuthenticatedAdmin
from app.services.laravel_auth_service import laravel_auth_service


async def get_bearer_token(authorization: str = Header(default="")) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token in Authorization header",
        )

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is empty",
        )
    return token


async def get_authenticated_admin(token: str = Header(default="", alias="Authorization")) -> AuthenticatedAdmin:
    bearer_token = await get_bearer_token(token)
    user = await laravel_auth_service.validate_token(bearer_token)

    return AuthenticatedAdmin(
        user_id=user.get("id"),
        user_email=user.get("email"),
        user=user,
        source="laravel-sanctum",
    )
