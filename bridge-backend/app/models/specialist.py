from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base, User


class Availability(str, enum.Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    VACATION = "vacation"


class LanguageProficiency(str, enum.Enum):
    BASIC = "basic"
    CONVERSATIONAL = "conversational"
    FLUENT = "fluent"
    NATIVE = "native"


class SpecialistProfile(Base):
    __tablename__ = "specialist_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True
    )
    headline: Mapped[str | None] = mapped_column(String(200), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    hourly_rate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    availability: Mapped[Availability] = mapped_column(
        Enum(Availability), default=Availability.AVAILABLE
    )
    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="specialist_profile")
    domains: Mapped[list["SpecialistDomain"]] = relationship(
        back_populates="specialist", cascade="all, delete-orphan"
    )
    languages: Mapped[list["SpecialistLanguage"]] = relationship(
        back_populates="specialist", cascade="all, delete-orphan"
    )
    competencies: Mapped[list["SpecialistCompetency"]] = relationship(
        back_populates="specialist", cascade="all, delete-orphan"
    )


class SpecialistDomain(Base):
    __tablename__ = "specialist_domains"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    specialist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("specialist_profiles.id")
    )
    domain: Mapped[str] = mapped_column(String, nullable=False)

    specialist: Mapped["SpecialistProfile"] = relationship(back_populates="domains")


class SpecialistLanguage(Base):
    __tablename__ = "specialist_languages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    specialist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("specialist_profiles.id")
    )
    language: Mapped[str] = mapped_column(String, nullable=False)
    proficiency: Mapped[LanguageProficiency] = mapped_column(
        Enum(LanguageProficiency), default=LanguageProficiency.FLUENT
    )

    specialist: Mapped["SpecialistProfile"] = relationship(back_populates="languages")


class SpecialistCompetency(Base):
    __tablename__ = "specialist_competencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    specialist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("specialist_profiles.id")
    )
    label: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    specialist: Mapped["SpecialistProfile"] = relationship(
        back_populates="competencies"
    )
