import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.lesson_plan import LessonPlanStatus


class LessonPlanGenerateRequest(BaseModel):
    room_id: uuid.UUID
    request_id: uuid.UUID | None = None
    additional_context: str | None = None


class LessonPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_id: uuid.UUID
    request_id: uuid.UUID | None = None
    specialist_id: uuid.UUID
    lesson_content: str
    practice_exercises: str
    homework: str
    language: str
    status: LessonPlanStatus
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
