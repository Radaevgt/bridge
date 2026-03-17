from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    service = AuthService(db)
    return await service.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    service = AuthService(db)
    return await service.refresh_tokens(data.refresh_token)
