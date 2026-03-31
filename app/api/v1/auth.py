from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth_dependencies import get_authenticated_admin
from app.schemas.auth_schemas import (
    AuthenticatedAdmin,
    LaravelLoginRequest,
    LaravelLoginResponse,
    TokenValidationResponse,
)
from app.services.laravel_auth_service import laravel_auth_service

router = APIRouter()


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
async def auth_me(admin: AuthenticatedAdmin = Depends(get_authenticated_admin)) -> TokenValidationResponse:
    """
    Validate the Sanctum token and return the authenticated admin profile.
    """
    return TokenValidationResponse(
        authenticated=True,
        user_id=admin.user_id,
        user_email=admin.user_email,
        user=admin.user,
        source=admin.source,
    )


@router.get("/protected-example", response_model=TokenValidationResponse)
async def protected_example(
    admin: AuthenticatedAdmin = Depends(get_authenticated_admin),
) -> TokenValidationResponse:
    """
    Example protected endpoint that you can copy to secure your business APIs.
    """
    return TokenValidationResponse(
        authenticated=True,
        user_id=admin.user_id,
        user_email=admin.user_email,
        user=admin.user,
        source=admin.source,
    )
