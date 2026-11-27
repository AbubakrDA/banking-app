from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    tenant_id: Optional[str] = Field(default=None, description="Optional tenant override for multi-tenant accounts")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    tenant_id: str
    role: str
    email: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    email: str
    full_name: str
    role: str
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    role: str = Field(default="agent", description="owner | admin | agent | customer")


class UserUpdateRole(BaseModel):
    role: str = Field(description="owner | admin | agent | customer")
