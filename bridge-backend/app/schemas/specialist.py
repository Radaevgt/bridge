import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.specialist import Availability, LanguageProficiency


class DomainSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    domain: str


class LanguageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    language: str
    proficiency: LanguageProficiency


class CompetencySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    label: str
    url: str
    display_order: int


class SpecialistUserSchema(BaseModel):
    """Nested user info included in specialist profile responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    avatar_url: str | None = None


class SpecialistProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    headline: str | None = None
    bio: str | None = None
    hourly_rate: float | None = None
    availability: Availability
    avg_rating: float
    review_count: int
    user: SpecialistUserSchema
    domains: list[DomainSchema] = []
    languages: list[LanguageSchema] = []
    competencies: list[CompetencySchema] = []
    relevance_score: float | None = None


class LanguageCreateSchema(BaseModel):
    """Typed schema for language input — replaces raw dict."""

    language: str
    proficiency: LanguageProficiency = LanguageProficiency.FLUENT


class SpecialistProfileCreate(BaseModel):
    headline: str | None = Field(None, max_length=200)
    bio: str | None = None
    hourly_rate: float | None = Field(None, ge=0)
    domains: list[str] = []
    languages: list[LanguageCreateSchema] = []


class CompetencyCreate(BaseModel):
    label: str = Field(min_length=1)
    url: str = Field(min_length=1)
    display_order: int = 0


class AvailabilityUpdate(BaseModel):
    availability: Availability
