import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.utils.jwt import create_access_token, create_refresh_token, decode_token
from app.utils.security import hash_password, verify_password


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register(self, data: RegisterRequest) -> TokenResponse:
        result = await self.db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        tokens = self._generate_tokens(user.id)
        return tokens

    async def login(self, data: LoginRequest) -> TokenResponse:
        result = await self.db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return self._generate_tokens(user.id)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        user_id = payload.get("sub")
        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return self._generate_tokens(user.id)

    @staticmethod
    def _generate_tokens(user_id: uuid.UUID) -> TokenResponse:
        access = create_access_token({"sub": str(user_id)})
        refresh = create_refresh_token({"sub": str(user_id)})
        return TokenResponse(access_token=access, refresh_token=refresh)
