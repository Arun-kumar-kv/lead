from typing import Any, Dict

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.schemas.auth_schemas import (
    LaravelLoginRequest,
    LaravelLoginResponse,
    TokenValidationResponse,
)
from app.services.laravel_auth_service import laravel_auth_service

router = APIRouter()


async def get_current_admin(authorization: str = Header(default="")) -> Dict[str, Any]:
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

    return await laravel_auth_service.validate_token(token)


def _extract_user_id(admin: Dict[str, Any]) -> int | None:
    user_id = admin.get("id")
    return user_id if isinstance(user_id, int) else None


def _extract_user_email(admin: Dict[str, Any]) -> str | None:
    user_email = admin.get("email")
    return user_email if isinstance(user_email, str) else None


@router.post("/login", response_model=LaravelLoginResponse)
async def auth_login(payload: LaravelLoginRequest) -> Dict[str, Any]:
    """
    Proxy Laravel login so FastAPI can always use the latest Sanctum token.
    """
    if not payload.username and not payload.email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide either username or email with password",
        )

    return await laravel_auth_service.login(
        password=payload.password,
        username=payload.username,
        email=payload.email,
    )


@router.get("/me", response_model=TokenValidationResponse)
async def auth_me(admin: Dict[str, Any] = Depends(get_current_admin)) -> TokenValidationResponse:
    """
    Validate the Sanctum token and return the authenticated admin profile.
    """
    return TokenValidationResponse(
        authenticated=True,
        user_id=_extract_user_id(admin),
        user_email=_extract_user_email(admin),
        user=admin,
    )


@router.get("/protected-example", response_model=TokenValidationResponse)
async def protected_example(
    admin: Dict[str, Any] = Depends(get_current_admin),
) -> TokenValidationResponse:
    """
    Example protected endpoint that you can copy to secure your business APIs.
    """
    return TokenValidationResponse(
        authenticated=True,
        user_id=_extract_user_id(admin),
        user_email=_extract_user_email(admin),
        user=admin,
    )
