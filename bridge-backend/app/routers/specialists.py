import uuid
import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.specialist import (
    AvailabilityUpdate,
    CompetencyCreate,
    CompetencySchema,
    SpecialistProfileCreate,
    SpecialistProfileResponse,
)
from app.services.specialist_service import SpecialistService
from app.utils.deps import require_specialist

router = APIRouter(prefix="/specialists", tags=["specialists"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MEDIA_DIR = Path(__file__).resolve().parent.parent.parent / "media" / "avatars"


@router.get("/", response_model=list[SpecialistProfileResponse])
async def search_specialists(
    search: str | None = None,
    domain: list[str] | None = Query(None),
    language: list[str] | None = Query(None),
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    availability_only: bool = False,
    sort: str = "rating",
    page: int = 1,
    db: AsyncSession = Depends(get_db),
) -> list[SpecialistProfileResponse]:
    service = SpecialistService(db)
    return await service.search(
        search=search,
        domain=domain,
        language=language,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        availability_only=availability_only,
        sort=sort,
        page=page,
    )


@router.get("/me", response_model=SpecialistProfileResponse | None)
async def get_my_profile(
    current_user: User = Depends(require_specialist),
    db: AsyncSession = Depends(get_db),
) -> SpecialistProfileResponse | None:
    service = SpecialistService(db)
    return await service.get_by_user_id(current_user.id)


@router.get("/{specialist_id}", response_model=SpecialistProfileResponse)
async def get_specialist(
    specialist_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> SpecialistProfileResponse:
    service = SpecialistService(db)
    profile = await service.get_by_id(specialist_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Specialist not found"
        )
    return profile


@router.post("/profile", response_model=SpecialistProfileResponse)
async def create_or_update_profile(
    data: SpecialistProfileCreate,
    current_user: User = Depends(require_specialist),
    db: AsyncSession = Depends(get_db),
) -> SpecialistProfileResponse:
    service = SpecialistService(db)
    return await service.create_or_update(current_user.id, data)


@router.post(
    "/competencies",
    response_model=CompetencySchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_competency(
    data: CompetencyCreate,
    current_user: User = Depends(require_specialist),
    db: AsyncSession = Depends(get_db),
) -> CompetencySchema:
    service = SpecialistService(db)
    return await service.add_competency(current_user.id, data)


@router.delete("/competencies/{competency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_competency(
    competency_id: uuid.UUID,
    current_user: User = Depends(require_specialist),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = SpecialistService(db)
    await service.delete_competency(current_user.id, competency_id)


@router.patch("/availability", response_model=SpecialistProfileResponse)
async def update_availability(
    data: AvailabilityUpdate,
    current_user: User = Depends(require_specialist),
    db: AsyncSession = Depends(get_db),
) -> SpecialistProfileResponse:
    service = SpecialistService(db)
    return await service.update_availability(current_user.id, data.availability)


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(require_specialist),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP images are allowed",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must not exceed 5 MB",
        )

    ext = file.content_type.split("/")[-1]
    if ext == "jpeg":
        ext = "jpg"
    filename = f"{current_user.id}_{int(time.time())}.{ext}"
    filepath = MEDIA_DIR / filename
    filepath.write_bytes(contents)

    avatar_url = f"/media/avatars/{filename}"
    current_user.avatar_url = avatar_url
    db.add(current_user)
    await db.commit()

    return {"avatar_url": avatar_url}
