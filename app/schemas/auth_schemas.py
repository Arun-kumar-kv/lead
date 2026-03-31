from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LaravelLoginRequest(BaseModel):
    username: Optional[str] = Field(None, description="Laravel admin username")
    email: Optional[str] = Field(None, description="Laravel admin email")
    password: str = Field(..., description="Laravel admin password")


class LaravelLoginResponse(BaseModel):
    status: bool
    message: str
    data: Dict[str, Any]
    token: str


class TokenValidationResponse(BaseModel):
    authenticated: bool
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    source: str = "laravel-sanctum"


class AuthenticatedAdmin(BaseModel):
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    user: Dict[str, Any]
    source: str = "laravel-sanctum"
