import uuid

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: UserRole
    full_name: str
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None
