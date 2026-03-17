import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review_service import ReviewService
from app.utils.deps import require_client

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "/{specialist_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    specialist_id: uuid.UUID,
    data: ReviewCreate,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    service = ReviewService(db)
    return await service.create_review(specialist_id, current_user.id, data)


@router.get("/{specialist_id}", response_model=list[ReviewResponse])
async def get_reviews(
    specialist_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ReviewResponse]:
    service = ReviewService(db)
    return await service.get_reviews(specialist_id)
