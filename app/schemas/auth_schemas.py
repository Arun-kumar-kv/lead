from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class LaravelLoginRequest(BaseModel):
    email: str = Field(..., description="Laravel admin email")
    password: str = Field(..., description="Laravel admin password")


class LaravelLoginResponse(BaseModel):
    status: bool
    message: str
    data: Dict[str, Any]
    token: str


class TokenValidationResponse(BaseModel):
    authenticated: bool
    user: Optional[Dict[str, Any]] = None
    source: str = "laravel-sanctum"
