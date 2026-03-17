import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.lesson_plan import (
    LessonPlanGenerateRequest,
    LessonPlanResponse,
)
from app.services.lesson_plan_service import LessonPlanService
from app.utils.deps import get_current_user, require_specialist

router = APIRouter(prefix="/lesson-plans", tags=["lesson_plans"])


@router.post(
    "/generate",
    response_model=LessonPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_lesson_plan(
    data: LessonPlanGenerateRequest,
    current_user: User = Depends(require_specialist),
    db: AsyncSession = Depends(get_db),
) -> LessonPlanResponse:
    service = LessonPlanService(db)
    plan = await service.generate_lesson_plan(current_user.id, data)
    return LessonPlanResponse.model_validate(plan)


@router.get(
    "/room/{room_id}",
    response_model=list[LessonPlanResponse],
)
async def get_room_lesson_plans(
    room_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LessonPlanResponse]:
    service = LessonPlanService(db)
    plans = await service.get_room_lesson_plans(room_id, current_user.id)
    return [LessonPlanResponse.model_validate(p) for p in plans]
