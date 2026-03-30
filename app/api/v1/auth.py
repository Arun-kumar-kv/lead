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


@router.post("/login", response_model=LaravelLoginResponse)
async def auth_login(payload: LaravelLoginRequest) -> Dict[str, Any]:
    """
    Proxy Laravel login so FastAPI can always use the latest Sanctum token.
    """
    return await laravel_auth_service.login(payload.email, payload.password)


@router.get("/me", response_model=TokenValidationResponse)
async def auth_me(admin: Dict[str, Any] = Depends(get_current_admin)) -> TokenValidationResponse:
    """
    Validate the Sanctum token and return the authenticated admin profile.
    """
    return TokenValidationResponse(authenticated=True, user=admin)


@router.get("/protected-example", response_model=TokenValidationResponse)
async def protected_example(
    admin: Dict[str, Any] = Depends(get_current_admin),
) -> TokenValidationResponse:
    """
    Example protected endpoint that you can copy to secure your business APIs.
    """
    return TokenValidationResponse(authenticated=True, user=admin)
