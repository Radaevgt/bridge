from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base, User


class Urgency(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RequestStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class TaskRequest(Base):
    __tablename__ = "task_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    urgency: Mapped[Urgency] = mapped_column(
        Enum(Urgency), default=Urgency.MEDIUM
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_min: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    budget_max: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), default=RequestStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    client: Mapped[User] = relationship(foreign_keys=[client_id])
    proposals: Mapped[list[TaskProposal]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )


class TaskProposal(Base):
    __tablename__ = "task_proposals"
    __table_args__ = (
        UniqueConstraint(
            "request_id", "specialist_id", name="uq_proposal_request_specialist"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_requests.id")
    )
    specialist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    price_offer: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    request: Mapped[TaskRequest] = relationship(back_populates="proposals")
    specialist: Mapped[User] = relationship(foreign_keys=[specialist_id])
