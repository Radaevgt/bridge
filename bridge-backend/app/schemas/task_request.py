import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task_request import RequestStatus, Urgency


# --- Nested info schemas ---


class ClientInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    avatar_url: str | None = None


class SpecialistInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    avatar_url: str | None = None


# --- Request schemas ---


class TaskRequestCreate(BaseModel):
    domain: str = Field(min_length=1)
    urgency: Urgency = Urgency.MEDIUM
    comment: str | None = None
    budget_min: float | None = Field(None, ge=0)
    budget_max: float | None = Field(None, ge=0)


class TaskRequestStatusUpdate(BaseModel):
    status: RequestStatus


# --- Response schemas ---


class TaskProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    specialist_id: uuid.UUID
    message: str
    price_offer: float | None = None
    created_at: datetime
    specialist: SpecialistInfo | None = None


class TaskRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    domain: str
    urgency: Urgency
    comment: str | None = None
    budget_min: float | None = None
    budget_max: float | None = None
    status: RequestStatus
    created_at: datetime
    updated_at: datetime
    client: ClientInfo | None = None
    proposals: list[TaskProposalResponse] = []
    proposal_count: int = 0


class TaskRequestListResponse(BaseModel):
    """Lighter version for list views (without full proposals)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    domain: str
    urgency: Urgency
    comment: str | None = None
    budget_min: float | None = None
    budget_max: float | None = None
    status: RequestStatus
    created_at: datetime
    updated_at: datetime
    client: ClientInfo | None = None
    proposal_count: int = 0


# --- Proposal request schema ---


class TaskProposalCreate(BaseModel):
    message: str = Field(min_length=1)
    price_offer: float | None = Field(None, ge=0)
